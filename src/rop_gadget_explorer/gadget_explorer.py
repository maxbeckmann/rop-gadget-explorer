import re
import typer

app = typer.Typer()

def search_gadget_family(family, in_file):
    for pattern in family:
        in_file.seek(0) # ensure we read from the start
        for line in in_file:
            res = re.search(pattern, line)
            if res:
                yield line.strip()

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
    

def _search_and_print(ctx, family):
    in_file = ctx.obj["file"]
    res = list(search_gadget_family(family, in_file))
    if res:
        print(str("\n").join(res))

@app.command()
def bkpt(ctx: typer.Context, dirty: bool = typer.Option(False, "--dirty", "-d")):
    clean = not dirty
    if clean:
        family = (
            f": int3 ; ret",
        )
    else:
        family = (
            f": int3 ; .* ret",
        )
    
    _search_and_print(ctx, family)

@app.command()
def set(ctx: typer.Context, r32, dirty: bool = typer.Option(False, "--dirty", "-d")):
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
    
    _search_and_print(ctx, family)

@app.command()
def move(ctx: typer.Context, src, dst, dirty: bool = typer.Option(False, "--dirty", "-d")):
    src = _check_register(src)
    dst = _check_register(dst)
    
    clean = not dirty
    if clean:
        family = (
            f": mov {dst}, {src} ; ret",
            f": push {src} ; pop {dst} ; ret",
            f": xchg {src}, {dst} ; ret",
            f": xchg {dst}, {src} ; ret",
        )
    else:
        family = (
            f": mov {dst}, {src} ;.* ret",
            f": push {src} ;((?!pop [^\s]).)* pop {dst} ;.* ret",
            f": xchg {src}, {dst} ;.* ret",
            f": xchg {dst}, {src} ;.* ret"
        )
    
    _search_and_print(ctx, family)

@app.command()
def sub(ctx: typer.Context, src, dst, dirty: bool = typer.Option(False, "--dirty", "-d")):
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
    
    _search_and_print(ctx, family)

@app.command()
def add(ctx: typer.Context, src, dst, dirty: bool = typer.Option(False, "--dirty", "-d")):
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
    
    _search_and_print(ctx, family)

@app.command()
def neg(ctx: typer.Context, dst, dirty: bool = typer.Option(False, "--dirty", "-d")):
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
    
    _search_and_print(ctx, family)

@app.command()
def inc(ctx: typer.Context, dst, dirty: bool = typer.Option(False, "--dirty", "-d")):
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
    
    _search_and_print(ctx, family)

@app.command()
def load(ctx: typer.Context, r32, ptr, dirty: bool = typer.Option(False, "--dirty", "-d")):
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
    
    _search_and_print(ctx, family)

@app.command()
def store(ctx: typer.Context, r32, ptr, offset: bool = typer.Option(False, "--offset", "-o"), dirty: bool = typer.Option(False, "--dirty", "-d")):
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
    
    _search_and_print(ctx, family)

@app.command()
def pushad(ctx: typer.Context, dirty: bool = typer.Option(False, "--dirty", "-d")):
    clean = not dirty
    if clean:
        family = (
            ": pushad ; ret",
        )
    else:
        family = (
            ": pushad ; .* ret",
        )
    
    _search_and_print(ctx, family)

@app.command()
def ret(ctx: typer.Context, dirty: bool = typer.Option(False, "--dirty", "-d")):
    clean = not dirty
    if clean:
        family = (
            ": ret ;",
        )
    else:
        family = (
            ": ret",
        )
    
    _search_and_print(ctx, family)

@app.callback()
def main(
    ctx: typer.Context, 
    gadgets: str = typer.Option("gadgets.txt", "--gadgets", "-g")
    ):
    ctx.ensure_object(dict)
    ctx.obj["file"] = open(gadgets, "r")

if __name__ == "__main__":
    app()