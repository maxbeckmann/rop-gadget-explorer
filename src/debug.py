from rop_gadget_explorer.cli import *
from rop_gadget_explorer.cli import _debug_print_result, _print_result
import rop_gadget_explorer.chains as c

in_file = open("test/data/libpal-gadgets.txt", "r")
res = c.move.build(in_file, register_a="r32", register_b="r32", allow_dirty=False)
_debug_print_result(res)