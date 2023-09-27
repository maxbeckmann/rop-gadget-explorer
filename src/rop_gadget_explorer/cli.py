import typer
from . import gadgets as g

app = typer.Typer()

def search_gadget_family(family, in_file):
    for pattern in family:
        in_file.seek(0) # ensure we read from the start
        for line in in_file:
            res = re.search(pattern, line)
            if res:
                yield line.strip()

def _print_result(res):
    if res:
        print(str("\n").join(res))

@app.command()
def bkpt(ctx: typer.Context, dirty: bool = typer.Option(False, "--dirty", "-d")): 
    in_file = ctx.obj["file"]
    res = g.bkpt(in_file, dirty)
    _print_result(res)

@app.command()
def set(ctx: typer.Context, r32, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = g.set(in_file, r32, dirty)
    _print_result(res)

@app.command()
def move(ctx: typer.Context, src, dst, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = g.move(in_file, src, dst, dirty)
    _print_result(res)

@app.command()
def xchg(ctx: typer.Context, src, dst, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = g.xchg(in_file, src, dst, dirty)
    _print_result(res)

@app.command()
def zero(ctx: typer.Context, target, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = g.zero(in_file, target, dirty)
    _print_result(res)

@app.command()
def sub(ctx: typer.Context, src, dst, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = g.sub(in_file, src, dst, dirty)
    _print_result(res)

@app.command()
def add(ctx: typer.Context, src, dst, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = g.add(in_file, src, dst, dirty)
    _print_result(res)

@app.command()
def neg(ctx: typer.Context, dst, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = g.neg(in_file, dst, dirty)
    _print_result(res)

@app.command()
def inc(ctx: typer.Context, dst, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = g.inc(in_file, dst, dirty)
    _print_result(res)

@app.command()
def load(ctx: typer.Context, r32, ptr, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = g.load(in_file, r32, ptr, dirty)
    _print_result(res)

@app.command()
def store(ctx: typer.Context, r32, ptr, offset: bool = typer.Option(False, "--offset", "-o"), dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = g.store(in_file, r32, ptr, dirty)
    _print_result(res)

@app.command()
def pushad(ctx: typer.Context, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = g.pushad(in_file, dirty)
    _print_result(res)

@app.command()
def ret(ctx: typer.Context, dirty: bool = typer.Option(False, "--dirty", "-d")):
    in_file = ctx.obj["file"]
    res = g.ret(in_file, dirty)
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