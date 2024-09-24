import unittest
import numpy as np

from utils.utils import fast_down_sample, fast_up_sample

class TestFastSample(unittest.TestCase):

    def setUp(self):
        # Create a sample image array
        self.large_images = np.random.randint(0, 256, (1, 128, 128, 3), dtype=np.uint8)
        self.small_images = np.random.randint(0, 256, (1, 64, 64, 3), dtype=np.uint8)
    
    def test_down_sample_max(self):
        small_images = fast_down_sample(self.large_images, by=2, method='max')
        self.assertEqual(small_images.shape, (1, 64, 64, 3))
    
    def test_down_sample_corner(self):
        small_images = fast_down_sample(self.large_images, by=2, method='corner')
        self.assertEqual(small_images.shape, (1, 64, 64, 3))
    
    def test_down_sample_mean(self):
        small_images = fast_down_sample(self.large_images, by=2, method='mean')
        self.assertEqual(small_images.shape, (1, 64, 64, 3))
    
    def test_down_sample_invalid_factor(self):
        with self.assertRaises(ValueError):
            fast_down_sample(self.large_images, by=3, method='max')
    
    def test_down_sample_invalid_shape(self):
        with self.assertRaises(ValueError):
            fast_down_sample(np.random.randint(0, 256, (128, 128, 3), dtype=np.uint8), by=2, method='max')
    
    def test_up_sample(self):
        large_images = fast_up_sample(self.small_images, by=2)
        self.assertEqual(large_images.shape, (1, 128, 128, 3))
    
    def test_up_sample_invalid_factor(self):
        with self.assertRaises(ValueError):
            fast_up_sample(self.small_images, by=0)
    
    def test_up_sample_invalid_shape(self):
        with self.assertRaises(ValueError):
            fast_up_sample(np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8), by=2)
    def test_unipotent(self):
        for method in ['max', 'mean', 'corner', 'nearest']:
            # upsample and downsample
            new_large_images = fast_up_sample(self.small_images, by=4)
            new_small_images = fast_down_sample(new_large_images, by=4, method=method)
            self.assertTrue(np.all(self.small_images == new_small_images))
            # upsample back
            new_large_images2 = fast_up_sample(new_small_images, by=4)
            self.assertTrue(np.all(new_large_images2 == new_large_images))


if __name__ == "__main__":
    unittest.main(argv=[''], exit=False)