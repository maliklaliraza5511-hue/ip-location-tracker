import unittest
import ipaddress

class IPValidationTests(unittest.TestCase):
    def test_public_test_ip_is_global(self):
        self.assertTrue(ipaddress.ip_address("8.8.8.8").is_global)

    def test_private_ip_is_not_global(self):
        self.assertFalse(ipaddress.ip_address("192.168.1.1").is_global)

    def test_invalid_ip_raises(self):
        with self.assertRaises(ValueError):
            ipaddress.ip_address("not-an-ip")

if __name__ == "__main__":
    unittest.main()
