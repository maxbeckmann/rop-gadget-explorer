import unittest

from src.rop_gadget_explorer import gadgets as g

gadget_file_libpal = open('test/data/libpal-gadgets.txt', "r")

class TestZeroGadgets(unittest.TestCase):
    
    example = '0x10014630: xor eax, eax ; ret ; (1 found)'
    dirty_example = '0x100862fa: xor eax, eax ; xor edx, edx ; ret ; (1 found)'
    edx_example = '0x100862fc: xor edx, edx ; ret ; (1 found)'
    
    def test_clear_eax(self):
        res = g.zero(gadget_file_libpal, "eax", False)
        self.assertIn(self.example, res)
        self.assertNotIn(self.dirty_example, res)
        self.assertNotIn(self.edx_example, res)
    
    def test_dirty_clear_eax(self):
        res = g.zero(gadget_file_libpal, "eax", True)
        self.assertIn(self.dirty_example, res)
        self.assertNotIn(self.edx_example, res)

    def test_clear_generic(self):
        res = g.zero(gadget_file_libpal, "r32", False)
        self.assertIn(self.example, res)
        self.assertIn(self.edx_example, res)
        self.assertNotIn(self.dirty_example, res)

if __name__ == '__main__':
    unittest.main()