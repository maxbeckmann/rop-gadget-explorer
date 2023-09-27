import re

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

def _check_register(r32):
    if r32 == "r32":
        r32 = "e.."
    else:
        assert r32 in registers
    return r32

def search_gadget_family(family, in_file):
    for pattern in family:
        in_file.seek(0) # ensure we read from the start
        for line in in_file:
            res = re.search(pattern, line)
            if res:
                yield line.strip()

def bkpt(in_file, dirty: bool):
    clean = not dirty
    if clean:
        family = (
            f": int3 ; ret",
        )
    else:
        family = (
            f": int3 ; .* ret",
        )
    
    return search_gadget_family(family, in_file)

def set(in_file, r32, dirty: bool):
    r32 = _check_register(r32)
    
    clean = not dirty
    if clean:
        family = (
            f": pop {r32} ; ret",
        )
    else:
        family = (
            f": pop {r32} ;.* ret",
        )
    
    return search_gadget_family(family, in_file)

def move(in_file, src, dst, dirty: bool):
    src = _check_register(src)
    dst = _check_register(dst)
    
    clean = not dirty
    if clean:
        family = (
            f": mov {dst}, {src} ; ret",
            f": push {src} ; pop {dst} ; ret",
        )
    else:
        family = (
            f": mov {dst}, {src} ;.* ret",
            f": push {src} ;((?!pop [^\s]).)* pop {dst} ;.* ret",
            f": xchg {src}, {dst} ;.* ret",
            f": xchg {dst}, {src} ;.* ret"
        )
    
    return search_gadget_family(family, in_file)

def xchg(in_file, src, dst, dirty: bool):
    src = _check_register(src)
    dst = _check_register(dst)
    
    clean = not dirty
    if clean:
        family = (
            f": xchg {src}, {dst} ; ret",
            f": xchg {dst}, {src} ; ret",
        )
    else:
        family = (
            f": xchg {src}, {dst} ;.* ret",
            f": xchg {dst}, {src} ;.* ret"
        )
    
    return search_gadget_family(family, in_file)

def zero(in_file, target, dirty: bool):
    target = _check_register(target)
    
    clean = not dirty
    if clean:
        family = (
            f": xor ({target}), \\1 ; ret",
        )
    else:
        family = (
            f": xor ({target}), \\1 ;.* ret",
        )
    
    return search_gadget_family(family, in_file)

def sub(in_file, src, dst, dirty: bool):
    src = _check_register(src)
    dst = _check_register(dst)
    
    clean = not dirty
    if clean:
        family = (
            f": sub {dst}, {src} ; ret",
        )
    else:
        family = (
            f": sub {dst}, {src} ;.* ret",
        )
    
    return search_gadget_family(family, in_file)

def add(in_file, src, dst, dirty: bool):
    src = _check_register(src)
    dst = _check_register(dst)
    
    clean = not dirty
    if clean:
        family = (
            f": add {dst}, {src} ; ret",
        )
    else:
        family = (
            f": add {dst}, {src} ;.* ret",
        )
    
    return search_gadget_family(family, in_file)

def neg(in_file, dst, dirty: bool):
    dst = _check_register(dst)
    
    clean = not dirty
    if clean:
        family = (
            f": neg {dst} ; ret",
        )
    else:
        family = (
            f": neg {dst} ;.* ret",
        )
    
    return search_gadget_family(family, in_file)

def inc(in_file, dst, dirty: bool):
    dst = _check_register(dst)
    
    clean = not dirty
    if clean:
        family = (
            f": inc {dst} ; ret",
        )
    else:
        family = (
            f": inc {dst} ;.* ret",
        )
    
    return search_gadget_family(family, in_file)

def load(in_file, r32, ptr, dirty: bool):
    ptr = _check_register(ptr)
    r32 = _check_register(r32)
    
    clean = not dirty
    if clean:
        family = (
            f": mov {r32},  \[{ptr}\] ; ret",
        )
    else:
        family = (
            f": mov {r32},  \[{ptr}\] ;.* ret",
        )
    
    return search_gadget_family(family, in_file)

def store(in_file, r32, ptr, offset: bool, dirty: bool):
    ptr = _check_register(ptr)
    r32 = _check_register(r32)
    
    clean = not dirty
    if clean:
        family = [
            f": mov  \[{ptr}\], {r32} ; ret",
        ]
        if offset:
            family += [f": mov  \[{ptr}+[\w]*\], {r32} ; ret"]
    else:
        family = [
            f": mov  \[{ptr}\], {r32} ;.* ret",
        ]
        if offset:
            family += [f": mov  \[{ptr}+[\w]*\], {r32} ;.* ret",]
    
    return search_gadget_family(family, in_file)

def pushad(in_file, dirty: bool):
    clean = not dirty
    if clean:
        family = (
            ": pushad ; ret",
        )
    else:
        family = (
            ": pushad ; .* ret",
        )
    
    return search_gadget_family(family, in_file)

def ret(in_file, dirty: bool):
    clean = not dirty
    if clean:
        family = (
            ": ret ;",
        )
    else:
        family = (
            ": ret",
        )
    
    return search_gadget_family(family, in_file)