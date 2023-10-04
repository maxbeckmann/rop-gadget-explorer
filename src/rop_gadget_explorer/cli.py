import typer
from . import gadgets as g
from .chains import *

app = typer.Typer()

def _print_result(res):
    if res:
        print(str("\n").join(map(str, res)))

def _debug_print_result(res):
    stack = []
    chain = next(res, None)
    while(chain):
        print(chain.stack)
        print(chain)
        print()
        chain = next(res, None)


def _iterate_file(family: g.Gadget, in_file, **kwargs):
    in_file.seek(0) # ensure we read from the start
    for line in in_file:
        res = family.from_string(line, **kwargs)
        if res:
            yield res

@app.command()
def bkpt(ctx: typer.Context, dirty: bool = typer.Option(False, "--dirty", "-d")): 
    in_file = ctx.obj["file"]
    res = _iterate_file(g.BreakpointGadget, in_file, allow_dirty=dirty)
    _print_result(res)

@app.command()
def set(ctx: typer.Context, r32, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = _iterate_file(g.SetRegisterGadget, in_file, target=r32, allow_dirty=dirty)
    _print_result(res)

@app.command()
def move(ctx: typer.Context, src, dst, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = MoveChainFactory().build(in_file, target_a=src, target_b=dst, allow_dirty=dirty)
    _print_result(res)

@app.command()
def xchg(ctx: typer.Context, src, dst, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = ExchangeChainFactory().build(in_file, target_a=src, target_b=dst, allow_dirty=dirty)
    _print_result(res)

@app.command()
def zero(ctx: typer.Context, target, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = _iterate_file(g.SetRegisterZeroGadget, in_file, target=target, allow_dirty=dirty)
    _print_result(res)

@app.command()
def sub(ctx: typer.Context, src, dst, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = _iterate_file(g.SubtractGadget, in_file, target_a=src, target_b=dst, allow_dirty=dirty)
    _print_result(res)

@app.command()
def add(ctx: typer.Context, src, dst, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = AdditionChainFactory.build(in_file, target_a=src, target_b=dst, allow_dirty=dirty)
    _print_result(res)

@app.command()
def neg(ctx: typer.Context, target, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = _iterate_file(g.NegateRegisterGadget, in_file, target=target, allow_dirty=dirty)
    _print_result(res)

@app.command()
def inc(ctx: typer.Context, target, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = _iterate_file(g.IncrementRegisterGadget, in_file, target=target, allow_dirty=dirty)
    _print_result(res)

@app.command()
def load(ctx: typer.Context, src, dst, offset: bool = typer.Option(False, "--no-offset", "-o"), dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = _iterate_file(g.LoadGadget, in_file, target_a=src, target_b=dst, allow_offset=not offset, allow_dirty=dirty)
    _print_result(res)

@app.command()
def store(ctx: typer.Context, src, dst, offset: bool = typer.Option(False, "--no-offset", "-o"), dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = _iterate_file(g.StoreGadget, in_file, target_a=src, target_b=dst, allow_offset=not offset, allow_dirty=dirty)
    _print_result(res)

@app.command()
def pushad(ctx: typer.Context, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = _iterate_file(g.PushadGadget, in_file, allow_dirty=dirty)
    _print_result(res)

@app.command()
def ret(ctx: typer.Context):
    in_file = ctx.obj["file"]
    res = _iterate_file(g.NopGadget, in_file, allow_dirty=False)
    _print_result(res)

@app.callback()
def main(
        ctx: typer.Context, 
        gadgets: str = typer.Option("gadgets.txt", "--gadgets", "-g")
    ):
    ctx.ensure_object(dict)
    ctx.obj["file"] = open(gadgets, "r")

if __name__ == "__main__":
    app()