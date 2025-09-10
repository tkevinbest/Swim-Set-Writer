# Swim Practice Set Writer

[![Tests](https://github.com/tkevinbest/Swim-Set-Writer/workflows/Quick%20Test/badge.svg)](https://github.com/tkevinbest/Swim-Set-Writer/actions)
[![Python Versions](https://github.com/tkevinbest/Swim-Set-Writer/workflows/Test%20Python%20Versions/badge.svg)](https://github.com/tkevinbest/Swim-Set-Writer/actions)
[![Windows](https://github.com/tkevinbest/Swim-Set-Writer/workflows/Windows%20Test/badge.svg)](https://github.com/tkevinbest/Swim-Set-Writer/actions)

A simple tool to write swimming workouts in plain text and generate professional PDFs.

## Quick Start

Write your workout in a `.prac` file:

```prac
title: Friday Morning Practice
units: yards
course: short

Warmup:
  200 swim @ 3:00
  200 kick @ 5:00

Main Set x3:
  4x75 rotating IM @ 1:15 [3x50 @ 1:25]
  2x50 stroke-free @ :50 [@ 1:00]

Cool Down:
  200 choice @ 4:00
```

Generate a PDF:
```bash
python generate_pdf.py workout.prac
```

**Result:** [Professional PDF with separate pages for different speed groups](./examples/example.pdf)

## Features

- **Simple syntax** - Write workouts in plain text
- **Multiple groups** - Include variations for swimmers of different speeds
- **Automatic calculations** - Total distances and times
- **Comments** - Add notes to sets and exercises

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Syntax

```
SET_NAME:
  [REPSx]DISTANCE DESCRIPTION [@ INTERVAL] [GROUP_VARIATION] # COMMENT
```

**Examples:**
- `200 swim @ 3:00` - 200 yards swim on a 3:00 min interval
- `4x50 kick @ :55` - 4x50s kick on a :55 s interval  
- `100 swim @ 1:30 [75 swim @ 1:45]` - Group A: 100y, Group B: 75y
- `Main Set x3:` - Repeat entire set 3 times

### Configuration

Add metadata at the top of your file:
```
title: Practice Name
author: Coach Name
units: yards          # or meters
course: short         # or long
date: 2025-01-15
```

### Commands

```bash
# View workout in terminal
python parse.py workout.prac

# Generate PDF
python generate_pdf.py workout.prac

# Custom filename and title
python generate_pdf.py workout.prac my_workout.pdf "Custom Title"
```

---

## Detailed Documentation

### Complete Syntax Reference

#### Line Structure
```
[REPSx]DISTANCE DESCRIPTION [@ INTERVAL] [GROUP_VARIATION] # COMMENT
```

- **REPSx**: Optional repetitions (e.g., `3x`, `8x`)
- **DISTANCE**: Required distance in meters/yards (e.g., `50`, `200`)
- **DESCRIPTION**: Required stroke/drill description (`swim`, `kick`, `pull`, `drill`, `easy`, etc.)
- **@ INTERVAL**: Optional intervals. Use "@" or "on" (e.g., `@ 1:30` or `on 1:30`)
- **GROUP_VARIATION**: Optional group-specific workout in brackets
- **# COMMENT**: Optional comment at end of line

#### Group Variations
Create different workouts for different swimmer speeds using bracket notation. These are optional and can include either different distances, intervals, descriptions, or any combinaion. 

```
# Different distances
100 swim @ 1:30 [75 swim @ 1:45]  # Group A: 100y, Group B: 75y

# Different repetitions  
4x25 sprint @ :30 [3x25 sprint @ :35]  # Group A: 4 reps, Group B: 3 reps

# Different strokes
100 freestyle @ 1:20 [100 backstroke @ 1:30]

# Concise variations - only specify what changes
4x75 rotating IM @ 1:15 [3x 50 @ 1:25] [2x 50 @ 1:30]
#   Group A: 4x75 rotating IM @ 1:15
#   Group B: 3x50 rotating IM @ 1:25 (inherits description)  
#   Group C: 2x50 rotating IM @ 1:30 (inherits description)

# Interval-only changes
2x50 stroke-free @ :50 [@ 1:00]
#   Group A: 2x50 stroke-free @ :50
#   Group B: 2x50 stroke-free @ 1:00 (inherits reps, distance, description)
```

#### Set Repetition
Add `xN:` to a header to repeat an entire set:
```
Main Set x3:  # This set will be done 3 times
  100 swim @ 1:30
  4x50 kick @ 1:00
```

#### Configuration Options
Add configuration at the top of your `.prac` file (must come before any sets):

- **Units**: `units: meters` or `units: yards` (can also use `m` or `y`)
- **Title**: `title: Practice Name` (appears in PDF header)
- **Author**: `author: Coach Name` (appears in PDF metadata)  
- **Date**: `date: 2025-09-09` (appears in PDF metadata)
- **Description**: `description: Practice description` (appears in PDF)
- **Level**: `level: Beginner/Intermediate/Advanced` (appears in PDF)
- **Course**: `course: short` or `course: long` (appears as "Pool: Short Course Meters" or "Pool: Long Course Yards")

#### Comments
- Lines starting with "#" are comments
- Comments can be placed at the end of lines after workout items
- Comments after set headers are included in the PDF output
- Blank lines are ignored

### Examples

#### Simple Workout
```
title: Basic Practice
units: meters
course: short

Warmup:
  400 swim @ 6:00
  200 kick @ 4:00

Main Set:
  5x100 swim @ 1:30
  200 easy @ 4:00

Cool Down:
  200 easy
```

#### Complex Workout with Group Variations
```
title: Multi-Group Training
author: Coach Smith
course: long
units: yards

Warmup:
  400 swim @ 6:00 [300 swim @ 7:00]  # B group shorter distance
  8x50 drill @ :50 [6x50 drill @ 1:00]  # B group fewer reps

Pre-Main x2:
  100 swim @ 1:20 [75 swim @ 1:30]  # build each 25
  2x50 kick @ :55 [2x25 kick @ 1:05]  # B group shorter distance

Main Set x3:
  100 swim @ 1:15 [75 swim @ 1:25]  # race pace
  4x25 sprint @ :30 [3x25 sprint @ :35]  # maximum effort
  100 easy @ 2:00 [75 easy @ 2:30]  # recovery

Cool Down:
  200 choice @ 4:00 [150 choice @ 4:00]
```

**Output:** This generates separate PDF pages - one for Group A and one for Group B, each showing only the relevant workout.

### Error Handling

The parser validates:
- Positive distances and repetitions
- Proper time format for intervals (MM:SS or H:MM:SS)
- Required descriptions for each item
- Proper indentation and structure
- Valid course values (short or long)
- Valid units (meters, yards, m, y)

Common error messages:
- `Distance must be positive`
- `Invalid interval format`
- `Invalid course: {course}. Must be 'short' or 'long'`
- `Invalid units: {units}. Must be 'meters', 'yards', 'm', or 'y'`
- `Item found outside of any set`
- `Could not parse item line`

## Contributing

Feel free to enhance the parser, add new features, or improve the PDF formatting!

### Project Structure

- `parse.py` - Core parser and workout analysis
- `generate_pdf.py` - PDF generation functionality  
- `README.md` - This documentation
- `requirements.txt` - Python dependencies
- `examples/example.prac` - Example workout file with all features
- `examples/example.pdf` - Generated PDF output
- `tests/` - Comprehensive unit test suite
  - `test_parse.py` - Parser functionality tests
  - `test_pdf_generator.py` - PDF generation tests  
  - `test_edge_cases.py` - Edge case and error handling tests
  - `run_tests.py` - Test runner script

### Running Tests

```bash
# Run all tests
python tests/run_tests.py

# Run specific test modules
python -m unittest tests.test_parse
python -m unittest tests.test_pdf_generator
python -m unittest tests.test_edge_cases
```

## Future Plans

### Web Interface (Streamlit Cloud)
We plan to deploy this as a web application on Streamlit Cloud, providing:
- **Online text editor** for writing .prac files
- **Real-time preview** of parsed workouts
- **One-click PDF generation** and download
- **Public sharing** via web URL
- **No installation required** - works in any browser

This will make the tool accessible to coaches and swimmers without needing to install Python or run commands locally.

