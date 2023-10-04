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


class SingleTargetGadget(Gadget):
    def __init__(self, string, register) -> None:
        super().__init__(string)
        self.register = register

    @classmethod
    def _insert_target(cls, patterns, target):
        result = []
        target = _translate_register(target)
        named_group_target = f"(?P<target>{target})"
        for pattern in patterns:
            updated_pattern = pattern.format(target=named_group_target)
            result.append(updated_pattern)
        return result

    @classmethod
    def from_string(cls, s, target, allow_dirty=False, **kwargs):
        patterns = cls._get_patterns(allow_dirty)
        updated_patterns = cls._insert_target(patterns, target)
        match = _match_patterns(updated_patterns, s)
        return cls._from_match(s, match)

    @classmethod
    def _from_match(cls, s, match):
        result = None
        if match:
            result = cls(
                s, 
                match.group("target"),
            )
        return result


class TwoTargetGadget(Gadget):
    def __init__(self, string, register_a, register_b) -> None:
        super().__init__(string)
        self.register_a = register_a
        self.register_b = register_b
    
    @classmethod
    def _insert_targets(cls, patterns, target_a, target_b):
        result = []
        target_a = _translate_register(target_a)
        target_b = _translate_register(target_b)
        named_group_target_a = f"(?P<src>{target_a})"
        named_group_target_b = f"(?P<dst>{target_b})"
        for pattern in patterns:
            updated_pattern = pattern.format(src=named_group_target_a, dst=named_group_target_b)
            result.append(updated_pattern)
        return result

    @classmethod
    def from_string(cls, s, target_a, target_b, allow_dirty=False, **kwargs):
        patterns = cls._get_patterns(allow_dirty)
        updated_patterns = cls._insert_targets(patterns, target_a, target_b)
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
    def _insert_targets_and_offset(cls, patterns, target_a, target_b, allow_offset: bool):
        result = []
        target_a = _translate_register(target_a)
        target_b = _translate_register(target_b)
        named_group_target_a = f"(?P<src>{target_a})"
        named_group_target_b = f"(?P<dst>{target_b})"

        named_group_offset = None
        if allow_offset:
            named_group_offset = "(?P<ost>[\+\-]0x\w+)?"
        else:
            named_group_offset = ""

        for pattern in patterns:
            updated_pattern = pattern.format(src=named_group_target_a, dst=named_group_target_b, offset=named_group_offset)
            result.append(updated_pattern)
        return result

    @classmethod
    def from_string(cls, s, target_a, target_b, allow_offset=False, allow_dirty=False, **kwargs):
        patterns = cls._get_patterns(allow_dirty)
        updated_patterns = cls._insert_targets_and_offset(patterns, target_a, target_b, allow_offset)
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


class MoveGadget(TwoTargetGadget):
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
                ": mov ({dst}), ({src}) ;.* ret",
                ": push ({src}) ;(?:(?:?!pop [^\s]).)* pop ({dst}) ;.* ret",
                ": xchg ({src}), ({dst}) ;.* ret",
                ": xchg ({dst}), ({src}) ;.* ret"
            )
        
        return result


class ExchangeRegisterGadget(TwoTargetGadget):
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
                ": xchg {src}, {dst} ;.* ret",
                ": xchg {dst}, {src} ;.* ret"
            )
        
        return result


class SetRegisterGadget(SingleTargetGadget):
    @classmethod
    def _get_patterns(cls, allow_dirty):
        result = None
    
        clean = not allow_dirty
        if clean:
            result = (
                ": pop ({target}) ; ret",
            )
        else:
            result = (
                ": pop ({target}) ;.* ret",
            )
        
        return result


class SetRegisterZeroGadget(SingleTargetGadget):
    @classmethod
    def _get_patterns(cls, allow_dirty):
        result = None
    
        clean = not allow_dirty
        if clean:
            result = (
                ": xor ({target}), \\1 ; ret",
            )
        else:
            result = (
                ": xor ({target}), \\1 ;.* ret",
            )
        
        return result


class SubtractGadget(TwoTargetGadget):
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
                ": sub {dst}, {src} ;.* ret",
            )
        
        return result


class AdditionGadget(TwoTargetGadget):
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
                ": add {dst}, {src} ;.* ret",
            )
        
        return result


class NegateRegisterGadget(SingleTargetGadget):
    @classmethod
    def _get_patterns(cls, allow_dirty):
        result = None
        
        clean = not allow_dirty
        if clean:
            result = (
                ": neg {target} ; ret",
            )
        else:
            result = (
                ": neg {target} ;.* ret",
            )
    
        return result


class IncrementRegisterGadget(SingleTargetGadget):
    @classmethod
    def _get_patterns(cls, allow_dirty):
        result = None
    
        clean = not allow_dirty
        if clean:
            result = (
                ": inc {target} ; ret",
            )
        else:
            result = (
                ": inc {target} ;.* ret",
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
                ": mov {dst},  \[{src}{offset}\] ;.* ret",
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
                ": mov  \[{dst}{offset}\], {src} ;.* ret",
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
                ": pushad ; .* ret",
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