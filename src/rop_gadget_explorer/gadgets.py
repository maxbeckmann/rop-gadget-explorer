import re
from abc import abstractclassmethod


registers = {
    "eax",
    "ebx",
    "ecx",
    "edx",
    "edi",
    "esi",
    "ebp",
    "esp",
    "r32",
}

def _translate_register(r32):
    if r32 == "r32":
        r32 = "e.."
    else:
        assert r32 in registers
    return r32

def _match_patterns(patterns, s):
    for pattern in patterns:
        res = re.search(pattern, s)
        if res:
            return res
    return None

class Gadget:
    def __init__(self, string: str) -> None:
        self.string = string.strip()
        split = self.string.split(":")
        self.address = int(split[0], base=16)
        self.instructions = list(map(str.strip, (split[1].split(";"))[:-1]))
    
    def __str__(self) -> str:
        return f"({hex(self.address)}) # {' ; '.join(self.instructions)}"
    
    @abstractclassmethod
    def _get_patterns(cls, allow_dirty):
        raise NotImplementedError()

    @classmethod
    def from_string(cls, s, allow_dirty=False, **kwargs):
        patterns = cls._get_patterns(allow_dirty)
        match = _match_patterns(patterns, s)
        return cls._from_match(s, match)
    
    @classmethod
    def _from_match(cls, s, match):
        result = None
        if match:
            result = cls(
                s, 
            )
        return result


class SingleRegisterGadget(Gadget):
    def __init__(self, string, register) -> None:
        super().__init__(string)
        self.register = register

    @classmethod
    def _insert_register(cls, patterns, register):
        result = []
        register = _translate_register(register)
        named_group_register = f"(?P<register>{register})"
        for pattern in patterns:
            updated_pattern = pattern.format(register=named_group_register)
            result.append(updated_pattern)
        return result

    @classmethod
    def from_string(cls, s, register, allow_dirty=False, **kwargs):
        patterns = cls._get_patterns(allow_dirty)
        updated_patterns = cls._insert_register(patterns, register)
        match = _match_patterns(updated_patterns, s)
        return cls._from_match(s, match)

    @classmethod
    def _from_match(cls, s, match):
        result = None
        if match:
            result = cls(
                s, 
                match.group("register"),
            )
        return result


class TwoRegisterGadget(Gadget):
    def __init__(self, string, register_a, register_b) -> None:
        super().__init__(string)
        self.register_a = register_a
        self.register_b = register_b
    
    @classmethod
    def _insert_registers(cls, patterns, register_a, register_b):
        result = []
        register_a = _translate_register(register_a)
        register_b = _translate_register(register_b)
        named_group_register_a = f"(?P<src>{register_a})"
        named_group_register_b = f"(?P<dst>{register_b})"
        for pattern in patterns:
            updated_pattern = pattern.format(src=named_group_register_a, dst=named_group_register_b)
            result.append(updated_pattern)
        return result

    @classmethod
    def from_string(cls, s, register_a, register_b, allow_dirty=False, **kwargs):
        patterns = cls._get_patterns(allow_dirty)
        updated_patterns = cls._insert_registers(patterns, register_a, register_b)
        match = _match_patterns(updated_patterns, s)
        return cls._from_match(s, match)

    @classmethod
    def _from_match(cls, s, match):
        result = None
        if match:
            result = cls(
                s, 
                match.group('src'),
                match.group('dst'),
            )
        return result


class LoadStoreGadget(Gadget):
    def __init__(self, string, register_ptr, register_value, offset) -> None:
        super().__init__(string)
        self.register_a = register_ptr
        self.register_b = register_value
        self.offset = offset
    
    @classmethod
    def _insert_registers_and_offset(cls, patterns, register_a, register_b, allow_offset: bool):
        result = []
        register_a = _translate_register(register_a)
        register_b = _translate_register(register_b)
        named_group_register_a = f"(?P<src>{register_a})"
        named_group_register_b = f"(?P<dst>{register_b})"

        named_group_offset = None
        if allow_offset:
            named_group_offset = "(?P<ost>[\+\-]0x\w+)?"
        else:
            named_group_offset = ""

        for pattern in patterns:
            updated_pattern = pattern.format(src=named_group_register_a, dst=named_group_register_b, offset=named_group_offset)
            result.append(updated_pattern)
        return result

    @classmethod
    def from_string(cls, s, register_a, register_b, allow_offset=False, allow_dirty=False, **kwargs):
        patterns = cls._get_patterns(allow_dirty)
        updated_patterns = cls._insert_registers_and_offset(patterns, register_a, register_b, allow_offset)
        match = _match_patterns(updated_patterns, s)
        return cls._from_match(s, match)

    @classmethod
    def _from_match(cls, s, match):
        result = None

        if match:
            offset = None
            try:
                offset_str = match.group('ost')
                if offset_str:
                    offset = int(offset_str, base=16)
            except IndexError:
                offset = 0

            result = cls(
                s, 
                match.group('src'),
                match.group('dst'),
                offset,
            )
        return result


class BreakpointGadget(Gadget):
    @classmethod
    def _get_patterns(cls, allow_dirty):
        result = None
        clean = not allow_dirty
        if clean:
            result = (
                f": int3 ; ret",
            )
        else:
            result = (
                f": int3 ; .* ret",
            )
        
        return result


class MoveGadget(TwoRegisterGadget):
    @classmethod
    def _get_patterns(cls, allow_dirty):
        result = None

        clean = not allow_dirty
        if clean:
            result = (
                ": mov ({dst}), ({src}) ; ret",
                ": push ({src}) ; pop ({dst}) ; ret",
            )
        else:
            result = (
                ": mov ({dst}), ({src}) ;.+ ret",
                ": push ({src}) ; .+ pop ({dst}) ;.* ret",
                ": push ({src}) ; .* pop ({dst}) ;.+ ret",
                ": xchg ({src}), ({dst}) ;.* ret",
                ": xchg ({dst}), ({src}) ;.* ret"
            )
        
        return result


class ExchangeRegisterGadget(TwoRegisterGadget):
    @classmethod
    def _get_patterns(cls, allow_dirty):
        result = None

        clean = not allow_dirty
        if clean:
            result = (
                ": xchg {src}, {dst} ; ret",
                ": xchg {dst}, {src} ; ret",
            )
        else:
            result = (
                ": xchg {src}, {dst} ;.+ ret",
                ": xchg {dst}, {src} ;.+ ret"
            )
        
        return result


class SetRegisterGadget(SingleRegisterGadget):
    @classmethod
    def _get_patterns(cls, allow_dirty):
        result = None
    
        clean = not allow_dirty
        if clean:
            result = (
                ": pop ({register}) ; ret",
            )
        else:
            result = (
                ": pop ({register}) ;.+ ret",
            )
        
        return result


class SetRegisterZeroGadget(SingleRegisterGadget):
    @classmethod
    def _get_patterns(cls, allow_dirty):
        result = None
    
        clean = not allow_dirty
        if clean:
            result = (
                ": xor ({register}), \\1 ; ret",
            )
        else:
            result = (
                ": xor ({register}), \\1 ;.+ ret",
            )
        
        return result


class SubtractGadget(TwoRegisterGadget):
    @classmethod
    def _get_patterns(cls, allow_dirty):
        result = None

        clean = not allow_dirty
        if clean:
            result = (
                ": sub {dst}, {src} ; ret",
            )
        else:
            result = (
                ": sub {dst}, {src} ;.+ ret",
            )
        
        return result


class AdditionGadget(TwoRegisterGadget):
    @classmethod
    def _get_patterns(cls, allow_dirty):
        result = None

        clean = not allow_dirty
        if clean:
            result = (
                ": add {dst}, {src} ; ret",
            )
        else:
            result = (
                ": add {dst}, {src} ;.+ ret",
            )
        
        return result


class NegateRegisterGadget(SingleRegisterGadget):
    @classmethod
    def _get_patterns(cls, allow_dirty):
        result = None
        
        clean = not allow_dirty
        if clean:
            result = (
                ": neg {register} ; ret",
            )
        else:
            result = (
                ": neg {register} ;.+ ret",
            )
    
        return result


class IncrementRegisterGadget(SingleRegisterGadget):
    @classmethod
    def _get_patterns(cls, allow_dirty):
        result = None
    
        clean = not allow_dirty
        if clean:
            result = (
                ": inc {register} ; ret",
            )
        else:
            result = (
                ": inc {register} ;.+ ret",
            )
        
        return result


class LoadGadget(LoadStoreGadget):
    @classmethod
    def _get_patterns(cls, allow_dirty):
        result = None

        clean = not allow_dirty    
        if clean:
            result = (
                ": mov {dst},  \[{src}{offset}\] ; ret",
            )
        else:
            result = (
                ": mov {dst},  \[{src}{offset}\] ;.+ ret",
            )
        
        return result


class StoreGadget(LoadStoreGadget):
    @classmethod
    def _get_patterns(cls, allow_dirty):
        result = None
    
        clean = not allow_dirty
        if clean:
            result = [
                ": mov  \[{dst}{offset}\], {src} ; ret",
            ]
        else:
            result = [
                ": mov  \[{dst}{offset}\], {src} ;.+ ret",
            ]
        
        return result


class PushadGadget(Gadget):
    @classmethod
    def _get_patterns(cls, allow_dirty):
        result = None
        clean = not allow_dirty
        if clean:
            result = (
                ": pushad ; ret",
            )
        else:
            result = (
                ": pushad ; .+ ret",
            )
    
        return result


class NopGadget(Gadget):
    @classmethod
    def _get_patterns(cls, allow_dirty):
        result = None
        clean = not allow_dirty
        if clean:
            result = (
                ": ret ;",
            )
        else:
            raise NotImplementedError()
        
        return result