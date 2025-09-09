"""
Unit tests for edge cases and error handling
"""

import unittest
import tempfile
import os
import sys

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parse import WorkoutConfig, PracticeSet, SetItem, parse_prac, validate_intervals


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def create_temp_file(self, content):
        """Helper to create temporary .prac file"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.prac', delete=False)
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    
    def test_empty_file(self):
        """Test parsing empty file"""
        content = ""
        temp_file = self.create_temp_file(content)
        
        try:
            config, sets = parse_prac(temp_file)
            self.assertEqual(config.units, "meters")  # Default
            self.assertEqual(len(sets), 0)
        finally:
            os.unlink(temp_file)
    
    def test_comments_only(self):
        """Test file with only comments"""
        content = """# This is a comment
# Another comment
# More comments
"""
        temp_file = self.create_temp_file(content)
        
        try:
            config, sets = parse_prac(temp_file)
            self.assertEqual(len(sets), 0)
        finally:
            os.unlink(temp_file)
    
    def test_invalid_distance(self):
        """Test parsing with invalid distance"""
        content = """units: meters

Warmup:
  0 swim @ 3:00
"""
        temp_file = self.create_temp_file(content)
        
        try:
            with self.assertRaises(ValueError) as context:
                parse_prac(temp_file)
            self.assertIn("Distance must be positive", str(context.exception))
        finally:
            os.unlink(temp_file)
    
    def test_invalid_reps(self):
        """Test parsing with invalid repetitions"""
        content = """units: meters

Warmup:
  0x100 swim @ 3:00
"""
        temp_file = self.create_temp_file(content)
        
        try:
            with self.assertRaises(ValueError) as context:
                parse_prac(temp_file)
            self.assertIn("Repetitions must be positive", str(context.exception))
        finally:
            os.unlink(temp_file)
    
    def test_empty_description(self):
        """Test parsing with empty description"""
        content = """units: meters

Warmup:
  100  @ 3:00
"""
        temp_file = self.create_temp_file(content)
        
        try:
            with self.assertRaises(ValueError) as context:
                parse_prac(temp_file)
            self.assertIn("Description cannot be empty", str(context.exception))
        finally:
            os.unlink(temp_file)
    
    def test_invalid_intervals(self):
        """Test parsing with invalid interval format"""
        content = """units: meters

Warmup:
  100 swim @ 999:00
"""
        temp_file = self.create_temp_file(content)
        
        try:
            with self.assertRaises(ValueError) as context:
                parse_prac(temp_file)
            self.assertIn("Invalid interval format", str(context.exception))
        finally:
            os.unlink(temp_file)
    
    def test_item_outside_set(self):
        """Test item definition outside of any set"""
        content = """units: meters

  100 swim @ 3:00  # This should be under a set header, not just indented
"""
        temp_file = self.create_temp_file(content)
        
        try:
            with self.assertRaises(ValueError) as context:
                parse_prac(temp_file)
            self.assertIn("Item found outside of any set", str(context.exception))
        finally:
            os.unlink(temp_file)
    
    def test_malformed_line(self):
        """Test completely malformed line"""
        content = """units: meters

Warmup:
  this is not a valid workout line
"""
        temp_file = self.create_temp_file(content)
        
        try:
            with self.assertRaises(ValueError) as context:
                parse_prac(temp_file)
            self.assertIn("Could not parse item line", str(context.exception))
        finally:
            os.unlink(temp_file)
    
    def test_unknown_metadata_field(self):
        """Test unknown metadata field (should warn but not fail)"""
        content = """unknown_field: some value
units: meters

Warmup:
  100 swim @ 2:00
"""
        temp_file = self.create_temp_file(content)
        
        try:
            # This should work but produce a warning
            config, sets = parse_prac(temp_file)
            self.assertEqual(config.units, "meters")
            self.assertEqual(len(sets), 1)
        finally:
            os.unlink(temp_file)
    
    def test_very_large_numbers(self):
        """Test with very large distance and repetition numbers"""
        content = """units: meters

Endurance Set:
  1x10000 swim @ 20:00
  100x100 swim @ 1:30
"""
        temp_file = self.create_temp_file(content)
        
        try:
            config, sets = parse_prac(temp_file)
            endurance_set = sets[0]
            # 1*10000 + 100*100 = 20000
            self.assertEqual(endurance_set.total_distance(), 20000)
        finally:
            os.unlink(temp_file)
    
    def test_multiple_intervals(self):
        """Test with many interval groups"""
        content = """units: meters

Multi-Group Set:
  100 swim @ 1:00/1:10/1:20/1:30/1:40
"""
        temp_file = self.create_temp_file(content)
        
        try:
            config, sets = parse_prac(temp_file)
            item = sets[0].items[0]
            self.assertEqual(len(item.intervals), 5)
            self.assertEqual(item.intervals[0], "1:00")
            self.assertEqual(item.intervals[4], "1:40")
        finally:
            os.unlink(temp_file)
    
    def test_mixed_indentation(self):
        """Test mixed tab and space indentation"""
        content = "units: meters\n\nWarmup:\n  100 swim @ 2:00\n\t200 kick @ 4:00\n"
        temp_file = self.create_temp_file(content)
        
        try:
            config, sets = parse_prac(temp_file)
            warmup = sets[0]
            self.assertEqual(len(warmup.items), 2)
            self.assertEqual(warmup.total_distance(), 300)
        finally:
            os.unlink(temp_file)


class TestValidationEdgeCases(unittest.TestCase):
    """Test validation function edge cases"""
    
    def test_empty_intervals_list(self):
        """Test validation with empty intervals list"""
        self.assertTrue(validate_intervals([]))
    
    def test_edge_time_formats(self):
        """Test edge cases for time format validation"""
        # Test boundary conditions
        self.assertTrue(validate_intervals([":00"]))  # Minimum
        self.assertTrue(validate_intervals([":59"]))  # Maximum seconds
        self.assertTrue(validate_intervals(["59:59"]))  # Maximum minutes
        
        # Test invalid boundaries  
        self.assertFalse(validate_intervals([":60"]))  # Invalid seconds
        self.assertFalse(validate_intervals(["60:00"]))  # Invalid minutes for MM:SS
    
    def test_mixed_valid_invalid_intervals(self):
        """Test list with both valid and invalid intervals"""
        self.assertFalse(validate_intervals(["1:30", "invalid", "2:00"]))
        self.assertTrue(validate_intervals(["1:30", "2:00", ":45"]))


if __name__ == '__main__':
    unittest.main()
