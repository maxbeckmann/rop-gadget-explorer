import unittest

from src.rop_gadget_explorer import gadgets as g

gadget_file_libpal = open('test/data/libpal-gadgets.txt', "r")

class TestZeroGadgets(unittest.TestCase):
    
    def test_clear_eax(self):
        example = '0x10014630: xor eax, eax ; ret ; (1 found)'
        dirty_example = '0x100862fa: xor eax, eax ; xor edx, edx ; ret ; (1 found)'
        
        res = g.zero(gadget_file_libpal, "eax", False)
        self.assertIn(example, res)
        self.assertNotIn(dirty_example, res)

        res = g.zero(gadget_file_libpal, "eax", True)
        self.assertIn(dirty_example, res)

if __name__ == '__main__':
    unittest.main()