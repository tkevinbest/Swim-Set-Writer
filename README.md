# Swim Practice Set Writer

A Python-based system to typeset swimming workouts into nicely formatted PDFs. The system parses custom `.prac` files that define workouts in a human-readable format and generates professional-looking workout sheets.

## Features

- **Human-readable format**: Easy to write and edit workout files
- **Multiple intervals**: Support for different speed groups (lanes A, B, C, etc.)
- **Automatic calculations**: Total distances, repetitions, time estimates, and set summaries
- **PDF generation**: Professional workout sheets with clean formatting and separate pages per group
- **Flexible group variations**: Concise syntax for group-specific modifications
- **Metadata support**: Title, author, date, description, and skill level
- **Set-level comments**: Comments after set headers are included in output
- **Validation**: Error checking for common mistakes in workout definitions
- **Unit configuration**: Support for both meters and yards
- **Comprehensive testing**: Full unit test suite included

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Writing Workout Files (.prac)

Create a plaintext file with a `.prac` extension using this format:

#### Basic Structure
- Each practice is divided into named sections (sets)
- Sets start with a header line ending with ":"
- Lines indented beneath headers define individual workout items
- Use spaces or tabs for indentation
- Optional configuration at the top of the file (must be first non-comment line)

#### Syntax Examples

```
# Sample practice file
units: meters

Warmup:
  200 swim @ 3:00/3:15
  100 kick @ 1:50/2:00

Main Set x2:
  100 swim @ 1:00/1:10
  3x50 kick @ :55/1:10
  4x25 drill @ :30 # fast turnover

Cool Down:
  100 easy
```

#### Line Structure
```
[REPSx]DISTANCE DESCRIPTION [@ INTERVAL1/INTERVAL2/...] [GROUP_VARIATION]
```

- **REPSx**: Optional repetitions (e.g., `3x`, `8x`)
- **DISTANCE**: Required distance in meters/yards (e.g., `50`, `200`)
- **DESCRIPTION**: Required stroke/drill description (`swim`, `kick`, `pull`, `drill`, `easy`, etc.)
- **@ INTERVAL**: Optional intervals. Use "/" to separate intervals for different groups (legacy format) or "on" instead of "@"
- **GROUP_VARIATION**: Optional group-specific workout in brackets (see Group Variations below)

#### Group Variations
Create different workouts for different skill groups using bracket notation. The main workout applies to Group A, with variations in brackets for Group B, C, etc.

**Basic Syntax:**
```
MAIN_WORKOUT [GROUP_B_VARIATION] [GROUP_C_VARIATION]
```

**Examples:**
```
# Different distances
100 swim @ 1:30 [75 swim @ 1:45]  # A: 100y, B: 75y

# Different repetitions  
4x25 sprint @ :30 [3x25 sprint @ :35]  # A: 4 reps, B: 3 reps

# Different strokes
100 freestyle @ 1:20 [100 backstroke @ 1:30]  # Different strokes

# Same workout for all groups (no brackets needed)
200 warmup @ 3:00
```

**PDF Output:** When group variations are present, the PDF generator creates separate pages for each group, showing only the relevant workout for that group.

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

```
# Complete metadata example
title: Friday Morning Practice
author: Coach Smith
date: 2025-09-09
description: Focus on IM technique and endurance
level: Intermediate
units: yards

Warmup:
  500 swim @ 8:00  # 500 yards
```

#### Comments
- Lines starting with "#" are comments
- Comments can be placed at the end of lines after workout items
- Comments after set headers are included in the PDF output
- Blank lines are ignored

#### Group Variations - Concise Syntax
You can now use concise syntax where unspecified parts inherit from the main workout:

```
# Concise variations - only specify what changes
4x75 rotating IM @ 1:15 [3x @ 1:25] [2x 50 @ 1:30]
#   Group A: 4x75 rotating IM @ 1:15
#   Group B: 3x75 rotating IM @ 1:25 (inherits distance & description)  
#   Group C: 2x50 rotating IM @ 1:30 (inherits description only)

# Interval-only changes
2x50 stroke-free @ :50 [@ 1:00]
#   Group A: 2x50 stroke-free @ :50
#   Group B: 2x50 stroke-free @ 1:00 (inherits reps, distance, description)
```

### Generating Output

#### View in Terminal
```bash
python parse.py example_set.prac
```

#### Generate PDF
```bash
# Basic PDF generation
python pdf_generator.py example_set.prac

# With custom output filename
python pdf_generator.py example_set.prac my_workout.pdf

# With custom title
python pdf_generator.py example_set.prac "Friday Morning Practice"
```

## File Examples

### Simple Workout
```
# Basic workout in meters
units: meters

Warmup:
  400 swim @ 6:00
  200 kick @ 4:00

Main Set:
  5x100 swim @ 1:30
  200 easy @ 4:00

Cool Down:
  200 easy
```

### Complex Workout with Group Variations
```
# Advanced workout with A and B group variations
title: Multi-Group Training
author: Coach Smith
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

## Project Structure

- `parse.py` - Core parser and workout analysis
- `pdf_generator.py` - PDF generation functionality  
- `README.md` - This documentation
- `requirements.txt` - Python dependencies
- `examples/example.prac` - Example workout file with all features
- `examples/example.pdf` - Generated PDF output
- `tests/` - Comprehensive unit test suite
  - `test_parse.py` - Parser functionality tests
  - `test_pdf_generator.py` - PDF generation tests  
  - `test_edge_cases.py` - Edge case and error handling tests
  - `run_tests.py` - Test runner script

## Running Tests

```bash
# Run all tests
python tests/run_tests.py

# Run specific test modules
python -m unittest tests.test_parse
python -m unittest tests.test_pdf_generator
python -m unittest tests.test_edge_cases
```

## Error Handling

The parser validates:
- Positive distances and repetitions
- Proper time format for intervals (MM:SS or H:MM:SS)
- Required descriptions for each item
- Proper indentation and structure

Common error messages:
- `Distance must be positive`
- `Invalid interval format`
- `Item found outside of any set`
- `Could not parse item line`

## Contributing

Feel free to enhance the parser, add new features, or improve the PDF formatting!