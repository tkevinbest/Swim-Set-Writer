"""
Unit tests for the swim practice parser
"""

import unittest
import tempfile
import os
from unittest.mock import patch
import sys

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parse import (
    WorkoutConfig, PracticeSet, SetItem, WorkoutSummary,
    parse_prac, validate_intervals
)


class TestWorkoutConfig(unittest.TestCase):
    """Test the WorkoutConfig class"""
    
    def test_default_config(self):
        """Test default configuration"""
        config = WorkoutConfig()
        self.assertEqual(config.units, "meters")
        self.assertEqual(config.unit_symbol, "m")
        self.assertIsNone(config.title)
        self.assertIsNone(config.author)
    
    def test_meters_config(self):
        """Test meters configuration"""
        config = WorkoutConfig(units="meters")
        self.assertEqual(config.units, "meters")
        self.assertEqual(config.unit_symbol, "m")
        
        config = WorkoutConfig(units="m")
        self.assertEqual(config.units, "meters")
        self.assertEqual(config.unit_symbol, "m")
    
    def test_yards_config(self):
        """Test yards configuration"""
        config = WorkoutConfig(units="yards")
        self.assertEqual(config.units, "yards")
        self.assertEqual(config.unit_symbol, "y")
        
        config = WorkoutConfig(units="y")
        self.assertEqual(config.units, "yards")
        self.assertEqual(config.unit_symbol, "y")
    
    def test_invalid_units(self):
        """Test invalid units raise error"""
        with self.assertRaises(ValueError):
            WorkoutConfig(units="kilometers")
    
    def test_course_validation(self):
        """Test course validation"""
        # Valid course values
        config1 = WorkoutConfig(course="short")
        self.assertEqual(config1.course, "Short Course")
        
        config2 = WorkoutConfig(course="long")
        self.assertEqual(config2.course, "Long Course")
        
        config3 = WorkoutConfig(course="SHORT")  # Test case insensitive
        self.assertEqual(config3.course, "Short Course")
        
        # Invalid course values
        with self.assertRaises(ValueError):
            WorkoutConfig(course="25")
        
        with self.assertRaises(ValueError):
            WorkoutConfig(course="olympic")
        
        # None course should be allowed
        config4 = WorkoutConfig(course=None)
        self.assertIsNone(config4.course)
    
    def test_metadata_fields(self):
        """Test metadata fields are stored correctly"""
        config = WorkoutConfig(
            units="yards",
            title="Test Workout",
            author="Coach Test",
            date="2024-01-01",
            description="A test workout",
            level="Beginner"
        )
        self.assertEqual(config.title, "Test Workout")
        self.assertEqual(config.author, "Coach Test")
        self.assertEqual(config.date, "2024-01-01")
        self.assertEqual(config.description, "A test workout")
        self.assertEqual(config.level, "Beginner")


class TestPracticeSet(unittest.TestCase):
    """Test the PracticeSet class"""
    
    def test_empty_set(self):
        """Test empty practice set"""
        practice_set = PracticeSet("Warmup")
        self.assertEqual(practice_set.name, "Warmup")
        self.assertEqual(practice_set.repeat, 1)
        self.assertEqual(practice_set.items, [])
        self.assertEqual(practice_set.total_distance(), 0)
    
    def test_set_with_items(self):
        """Test practice set with items"""
        items = [
            SetItem(1, 200, "swim", ["3:00"]),
            SetItem(3, 50, "kick", ["1:00"])
        ]
        practice_set = PracticeSet("Main Set", repeat=2, items=items)
        self.assertEqual(practice_set.name, "Main Set")
        self.assertEqual(practice_set.repeat, 2)
        self.assertEqual(len(practice_set.items), 2)
        self.assertEqual(practice_set.total_distance(), 700)  # (200 + 3*50) * 2


class TestSetItem(unittest.TestCase):
    """Test the SetItem class"""
    
    def test_basic_item(self):
        """Test basic set item"""
        item = SetItem(1, 100, "swim", ["1:30"])
        self.assertEqual(item.reps, 1)
        self.assertEqual(item.distance, 100)
        self.assertEqual(item.desc, "swim")
        self.assertEqual(item.intervals, ["1:30"])
        self.assertEqual(item.total_distance(), 100)
    
    def test_multiple_reps(self):
        """Test item with multiple repetitions"""
        item = SetItem(4, 25, "sprint", ["0:30"])
        self.assertEqual(item.total_distance(), 100)
    
    def test_item_with_note(self):
        """Test item with note"""
        item = SetItem(1, 50, "kick", ["1:00"], note="hard effort")
        self.assertEqual(item.note, "hard effort")
    
    def test_item_string_representation(self):
        """Test string representation of item"""
        item = SetItem(3, 50, "kick", ["0:55", "1:10"], note="fast tempo")
        str_repr = str(item)
        self.assertIn("3x50", str_repr)
        self.assertIn("kick", str_repr)
        self.assertIn("0:55/1:10", str_repr)
        self.assertIn("fast tempo", str_repr)


class TestValidateIntervals(unittest.TestCase):
    """Test interval validation function"""
    
    def test_valid_intervals(self):
        """Test valid interval formats"""
        valid_intervals = [
            [":30"],
            ["1:00"],
            ["1:30"],
            ["12:00"],
            ["0:45"],
            [":30", "1:00"],
            ["1:15", "1:30"]
        ]
        
        for intervals in valid_intervals:
            with self.subTest(intervals=intervals):
                self.assertTrue(validate_intervals(intervals))
    
    def test_invalid_intervals(self):
        """Test invalid interval formats"""
        invalid_intervals = [
            ["60"],  # No colon
            ["1:60"],  # Invalid seconds
            ["60:00"],  # Invalid minutes for MM:SS format
            ["1:1"],  # Single digit seconds
            [":1"],  # Single digit with colon prefix
            ["1.30"],  # Wrong separator
            ["abc"],  # Non-numeric
        ]
        
        for intervals in invalid_intervals:
            with self.subTest(intervals=intervals):
                self.assertFalse(validate_intervals(intervals))


class TestParsePrac(unittest.TestCase):
    """Test the main parsing function"""
    
    def create_temp_file(self, content):
        """Helper to create temporary .prac file"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.prac', delete=False)
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    
    def tearDown(self):
        """Clean up temporary files"""
        # Clean up any temp files created during tests
        pass
    
    def test_basic_parsing(self):
        """Test basic file parsing"""
        content = """# Test workout
units: meters

Warmup:
  200 swim @ 3:00
  100 kick @ 2:00

Cool Down:
  100 easy
"""
        temp_file = self.create_temp_file(content)
        
        try:
            config, sets = parse_prac(temp_file)
            
            self.assertEqual(config.units, "meters")
            self.assertEqual(len(sets), 2)
            
            # Test Warmup set
            warmup = sets[0]
            self.assertEqual(warmup.name, "Warmup")
            self.assertEqual(len(warmup.items), 2)
            self.assertEqual(warmup.total_distance(), 300)
            
            # Test Cool Down set
            cooldown = sets[1]
            self.assertEqual(cooldown.name, "Cool Down")
            self.assertEqual(len(cooldown.items), 1)
            self.assertEqual(cooldown.total_distance(), 100)
            
        finally:
            os.unlink(temp_file)
    
    def test_metadata_parsing(self):
        """Test parsing with full metadata"""
        content = """# Test workout with metadata
title: Test Practice
author: Coach Test
date: 2024-01-01
level: Intermediate
description: Test workout for unit tests
units: yards

Main Set:
  100 swim @ 1:30
"""
        temp_file = self.create_temp_file(content)
        
        try:
            config, sets = parse_prac(temp_file)
            
            self.assertEqual(config.title, "Test Practice")
            self.assertEqual(config.author, "Coach Test")
            self.assertEqual(config.date, "2024-01-01")
            self.assertEqual(config.level, "Intermediate")
            self.assertEqual(config.description, "Test workout for unit tests")
            self.assertEqual(config.units, "yards")
            
        finally:
            os.unlink(temp_file)
    
    def test_set_repetition(self):
        """Test set repetition parsing"""
        content = """units: meters

Main Set x3:
  100 swim @ 1:30
  2x50 kick @ 1:00
"""
        temp_file = self.create_temp_file(content)
        
        try:
            config, sets = parse_prac(temp_file)
            
            main_set = sets[0]
            self.assertEqual(main_set.name, "Main Set")
            self.assertEqual(main_set.repeat, 3)
            self.assertEqual(main_set.total_distance(), 600)  # (100 + 2*50) * 3
            
        finally:
            os.unlink(temp_file)
    
    def test_comments_and_notes(self):
        """Test parsing comments and inline notes"""
        content = """units: meters
# This is a comment

Warmup:
  200 swim @ 3:00  # easy pace
  100 kick @ 2:00  # build effort
"""
        temp_file = self.create_temp_file(content)
        
        try:
            config, sets = parse_prac(temp_file)
            
            warmup = sets[0]
            self.assertEqual(warmup.items[0].note, "easy pace")
            self.assertEqual(warmup.items[1].note, "build effort")
            
        finally:
            os.unlink(temp_file)
    
    def test_file_not_found(self):
        """Test parsing non-existent file"""
        with self.assertRaises(FileNotFoundError):
            parse_prac("nonexistent_file.prac")
    
    def test_invalid_syntax(self):
        """Test parsing with invalid syntax"""
        content = """units: meters

Warmup:
  invalid line without distance
"""
        temp_file = self.create_temp_file(content)
        
        try:
            with self.assertRaises(ValueError):
                parse_prac(temp_file)
        finally:
            os.unlink(temp_file)


class TestWorkoutSummary(unittest.TestCase):
    """Test the WorkoutSummary class"""
    
    def test_summary_calculation(self):
        """Test workout summary calculations"""
        config = WorkoutConfig(units="meters", title="Test Workout")
        
        items1 = [SetItem(1, 200, "swim", ["3:00"])]
        items2 = [SetItem(4, 50, "kick", ["1:00"])]
        
        sets = [
            PracticeSet("Warmup", repeat=1, items=items1),
            PracticeSet("Main Set", repeat=2, items=items2)
        ]
        
        summary = WorkoutSummary(config, sets)
        self.assertEqual(summary.total_distance(), 600)  # 200 + (4*50)*2
    
    def test_summary_formatting(self):
        """Test workout summary formatting"""
        config = WorkoutConfig(units="yards", title="Test Workout", author="Coach Test")
        
        items = [SetItem(1, 100, "swim", ["1:30"])]
        sets = [PracticeSet("Test Set", repeat=1, items=items)]
        
        summary = WorkoutSummary(config, sets)
        formatted = summary.format_workout()
        
        self.assertIn("TEST WORKOUT", formatted)
        self.assertIn("Coach: Coach Test", formatted)
        self.assertIn("Units: Yards", formatted)
        self.assertIn("100 y", formatted)


if __name__ == '__main__':
    unittest.main()
