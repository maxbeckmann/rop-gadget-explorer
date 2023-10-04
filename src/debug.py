from rop_gadget_explorer.cli import *
from rop_gadget_explorer.cli import _debug_print_result, _print_result
import rop_gadget_explorer.chains as c

in_file = open("test/data/libpal-gadgets.txt", "r")
res = c.add.build(in_file, target_a="r32", target_b="r32", allow_dirty=False)
print()
print()
print()
_print_result(res)