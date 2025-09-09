"""
Unit tests for the PDF generator
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdf_generator import PDFWorkoutGenerator
from parse import WorkoutConfig, PracticeSet, SetItem


class TestPDFWorkoutGenerator(unittest.TestCase):
    """Test the PDF generator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = PDFWorkoutGenerator()
        self.config = WorkoutConfig(
            units="meters",
            title="Test Workout",
            author="Coach Test",
            date="2024-01-01",
            level="Advanced",
            description="Test description"
        )
        
        # Create sample workout data
        items1 = [
            SetItem(1, 200, "swim", ["3:00", "3:30"], note="easy pace"),
            SetItem(4, 50, "kick", ["1:00"])
        ]
        items2 = [
            SetItem(2, 100, "swim", ["1:30"], note="build effort")
        ]
        
        self.sets = [
            PracticeSet("Warmup", repeat=1, items=items1),
            PracticeSet("Main Set", repeat=3, items=items2)
        ]
    
    def test_generator_initialization(self):
        """Test PDF generator initialization"""
        self.assertIsNotNone(self.generator.styles)
        self.assertIn('WorkoutTitle', self.generator.styles)
        self.assertIn('SetHeader', self.generator.styles)
        self.assertIn('SetItem', self.generator.styles)
        self.assertIn('Summary', self.generator.styles)
    
    @patch('pdf_generator.SimpleDocTemplate')
    def test_generate_pdf_basic(self, mock_doc_class):
        """Test basic PDF generation"""
        mock_doc = MagicMock()
        mock_doc_class.return_value = mock_doc
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        temp_file.close()
        
        try:
            self.generator.generate_pdf(self.config, self.sets, temp_file.name)
            
            # Verify document was created with correct parameters
            mock_doc_class.assert_called_once()
            call_args = mock_doc_class.call_args
            
            # Check filename
            self.assertEqual(call_args[0][0], temp_file.name)
            
            # Check metadata parameters
            self.assertEqual(call_args[1]['title'], "Test Workout")
            self.assertEqual(call_args[1]['author'], "Coach Test")
            self.assertEqual(call_args[1]['subject'], "Test description")
            
            # Verify build was called
            mock_doc.build.assert_called_once()
            
        finally:
            os.unlink(temp_file.name)
    
    @patch('pdf_generator.SimpleDocTemplate')
    def test_generate_pdf_with_comments(self, mock_doc_class):
        """Test PDF generation with comments"""
        mock_doc = MagicMock()
        mock_doc_class.return_value = mock_doc
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        temp_file.close()
        
        try:
            self.generator.generate_pdf(self.config, self.sets, temp_file.name)
            
            # Verify build was called with story containing comments
            mock_doc.build.assert_called_once()
            story = mock_doc.build.call_args[0][0]
            
            # Should have content (we can't easily test exact content without mocking more)
            self.assertGreater(len(story), 0)
            
        finally:
            os.unlink(temp_file.name)
    
    def test_generate_from_file_missing(self):
        """Test generating from non-existent file"""
        with self.assertRaises(FileNotFoundError):
            self.generator.generate_from_file("nonexistent.prac")
    
    @patch('parse.parse_prac')
    @patch('pdf_generator.PDFWorkoutGenerator.generate_pdf')
    def test_generate_from_file_success(self, mock_generate, mock_parse):
        """Test successful generation from file"""
        mock_parse.return_value = (self.config, self.sets)
        
        temp_prac = tempfile.NamedTemporaryFile(mode='w', suffix='.prac', delete=False)
        temp_prac.write("units: meters\nWarmup:\n  100 swim @ 2:00")
        temp_prac.close()
        
        try:
            output_file = self.generator.generate_from_file(temp_prac.name)
            
            # Verify parsing was called
            mock_parse.assert_called_once_with(temp_prac.name)
            
            # Verify PDF generation was called
            mock_generate.assert_called_once()
            call_args = mock_generate.call_args
            self.assertEqual(call_args[0][0], self.config)
            self.assertEqual(call_args[0][1], self.sets)
            
            # Check output filename
            expected_output = temp_prac.name.replace('.prac', '.pdf')
            self.assertEqual(output_file, expected_output)
            
        finally:
            os.unlink(temp_prac.name)
    
    @patch('parse.parse_prac')
    @patch('pdf_generator.PDFWorkoutGenerator.generate_pdf')
    def test_generate_with_custom_title(self, mock_generate, mock_parse):
        """Test generation with custom title override"""
        mock_parse.return_value = (self.config, self.sets)
        
        temp_prac = tempfile.NamedTemporaryFile(mode='w', suffix='.prac', delete=False)
        temp_prac.write("units: meters\nWarmup:\n  100 swim @ 2:00")
        temp_prac.close()
        
        try:
            custom_title = "Custom Workout Title"
            self.generator.generate_from_file(temp_prac.name, title=custom_title)
            
            # Verify PDF generation was called with custom title
            mock_generate.assert_called_once()
            call_args = mock_generate.call_args
            self.assertEqual(call_args[1]['title'], custom_title)
            
        finally:
            os.unlink(temp_prac.name)


class TestPDFIntegration(unittest.TestCase):
    """Integration tests for PDF generation"""
    
    def test_full_pdf_generation(self):
        """Test complete PDF generation process"""
        # Create a simple workout file
        content = """title: Integration Test
author: Test Suite
date: 2024-01-01
units: meters

Warmup:
  200 swim @ 3:00  # easy
  100 kick @ 2:00

Main Set x2:
  100 swim @ 1:30
  4x25 sprint @ 0:30  # all out

Cool Down:
  100 easy
"""
        
        temp_prac = tempfile.NamedTemporaryFile(mode='w', suffix='.prac', delete=False)
        temp_prac.write(content)
        temp_prac.close()
        
        temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        temp_pdf.close()
        
        try:
            generator = PDFWorkoutGenerator()
            output_file = generator.generate_from_file(temp_prac.name, temp_pdf.name)
            
            # Verify PDF file was created
            self.assertTrue(os.path.exists(output_file))
            self.assertGreater(os.path.getsize(output_file), 0)
            
        finally:
            os.unlink(temp_prac.name)
            if os.path.exists(temp_pdf.name):
                os.unlink(temp_pdf.name)


if __name__ == '__main__':
    unittest.main()
