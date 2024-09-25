import unittest
import numpy as np

from utils.utils import fast_down_sample, fast_up_sample

class TestFastSample(unittest.TestCase):

    def setUp(self):
        # Create a sample image array
        self.methods = ['max', 'corner', 'nearest','mean']
        self.by = 4
        self.small_shape = (1, 64, 32, 3)
        self.large_shape = (self.small_shape[0],
                            self.small_shape[1]*self.by,
                            self.small_shape[2]*self.by,
                            self.small_shape[3])
        self.large_images = np.random.randint(0, 256, self.large_shape, dtype=np.uint8)
        self.small_images = np.random.randint(0, 256, self.small_shape, dtype=np.uint8)
    
    def test_down_sample(self):
        for method in self.methods:
            small_images = fast_down_sample(self.large_images, by=self.by, method=method)
            self.assertEqual(small_images.shape, self.small_shape, msg=method)
        
    
     
    def test_down_sample_invalid_factor(self):
        with self.assertRaises(ValueError):
            fast_down_sample(self.large_images, by=3, method='max')
    
    def test_down_sample_invalid_shape(self):
        with self.assertRaises(ValueError):
            fast_down_sample(np.random.randint(0, 256, (128, 128, 3), dtype=np.uint8), by=self.by, method='max')
    
    def test_up_sample(self):
        large_images = fast_up_sample(self.small_images, by=self.by)
        self.assertEqual(large_images.shape, self.large_shape)
    
    def test_up_sample_invalid_factor(self):
        with self.assertRaises(ValueError):
            fast_up_sample(self.small_images, by=0)
    
    def test_up_sample_invalid_shape(self):
        with self.assertRaises(ValueError):
            fast_up_sample(np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8), by=self.by)
    
    def test_unipotent(self):
        for method in ['max',  'corner', 'nearest', 'mean',]:
            # upsample and downsample
            a = fast_up_sample(self.small_images, by=self.by)
            b = fast_down_sample(a, by=self.by, method=method)
            c = fast_up_sample(b, by=self.by)
            # 
            self.assertEqual(self.small_shape, b.shape, msg=method)
            self.assertTrue(np.all(self.small_images == b), msg=method)
            # upsample back
            
            self.assertEqual(a.shape, c.shape, msg=method)
            self.assertTrue(np.all(a == c), msg=method+"/err_max:"+str(np.max(np.abs(a-c))))


if __name__ == "__main__":
    unittest.main(argv=[''], exit=False)