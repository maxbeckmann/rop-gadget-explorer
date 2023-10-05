import typer
from rop_gadget_explorer import gadgets as g
from rop_gadget_explorer import chains

app = typer.Typer()

def _print_result(res):
    for chain in res:
        print(chain)

def _iterate_file(family: g.Gadget, in_file, **kwargs):
    in_file.seek(0) # ensure we read from the start
    for line in in_file:
        res = family.from_string(line, **kwargs)
        if res:
            yield res

@app.command()
def bkpt(ctx: typer.Context, dirty: bool = typer.Option(False, "--dirty", "-d")): 
    in_file = ctx.obj["file"]
    res = chains.bkpt.build(in_file, allow_dirty=dirty)
    _print_result(res)

@app.command()
def set(ctx: typer.Context, r32, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = chains.setv.build(in_file, register=r32, allow_dirty=dirty)
    _print_result(res)

@app.command()
def move(ctx: typer.Context, src, dst, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = chains.move.build(in_file, register_a=src, register_b=dst, allow_dirty=dirty)
    _print_result(res)

@app.command()
def xchg(ctx: typer.Context, src, dst, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = chains.xchg.build(in_file, register_a=src, register_b=dst, allow_dirty=dirty)
    _print_result(res)

@app.command()
def zero(ctx: typer.Context, target, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = chains.zero.build(in_file, register=target, allow_dirty=dirty)
    _print_result(res)

@app.command()
def sub(ctx: typer.Context, src, dst, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = chains.sub.build(in_file, register_a=src, register_b=dst, allow_dirty=dirty)
    _print_result(res)

@app.command()
def add(ctx: typer.Context, src, dst, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = chains.add.build(in_file, register_a=src, register_b=dst, allow_dirty=dirty)
    _print_result(res)

@app.command()
def neg(ctx: typer.Context, target, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = chains.neg.build(in_file, register=target, allow_dirty=dirty)
    _print_result(res)

@app.command()
def inc(ctx: typer.Context, target, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = chains.inc.build(in_file, register=target, allow_dirty=dirty)
    _print_result(res)

@app.command()
def load(ctx: typer.Context, src, dst, offset: bool = typer.Option(False, "--no-offset", "-o"), dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = chains.load.build(in_file, register_a=src, register_b=dst, allow_offset=not offset, allow_dirty=dirty)
    _print_result(res)

@app.command()
def store(ctx: typer.Context, src, dst, offset: bool = typer.Option(False, "--no-offset", "-o"), dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = chains.store.build(in_file, register_a=src, register_b=dst, allow_offset=not offset, allow_dirty=dirty)
    _print_result(res)

@app.command()
def pushad(ctx: typer.Context, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = chains.pushd.build(in_file, allow_dirty=dirty)
    _print_result(res)

@app.command()
def ret(ctx: typer.Context):
    in_file = ctx.obj["file"]
    res = chains.ret.build(in_file, allow_dirty=False)
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