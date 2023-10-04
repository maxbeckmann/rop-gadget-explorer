from rop_gadget_explorer.cli import *
from rop_gadget_explorer.cli import _print_result

in_file = open("test/data/libpal-gadgets.txt", "r")
res = MoveChainFactory().build(in_file, target_a="r32", target_b="r32", allow_dirty=False)
_print_result(res)