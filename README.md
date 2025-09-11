# Swim Practice Set Writer

[![Tests](https://github.com/tkevinbest/Swim-Set-Writer/workflows/Quick%20Test/badge.svg)](https://github.com/tkevinbest/Swim-Set-Writer/actions)
[![Python Versions](https://github.com/tkevinbest/Swim-Set-Writer/workflows/Test%20Python%20Versions/badge.svg)](https://github.com/tkevinbest/Swim-Set-Writer/actions)
[![Windows](https://github.com/tkevinbest/Swim-Set-Writer/workflows/Windows%20Test/badge.svg)](https://github.com/tkevinbest/Swim-Set-Writer/actions)

A simple tool to write swimming workouts in plain text and generate well-formatted PDFs.

## Quick Start
The easiest way to use the swim set practice writer tool is via the [web app](https://swim-set-writer.streamlit.app). No installation required! 

## Features
- **Simple syntax** - Write workouts in plain text
- **Multiple groups** - Easily include variations for swimmers of different speeds
- **Automatic calculations** - Total distances and times
- **Comments** - Add notes to sets and exercises
- **Clean output** - Well-formatted PDFs with proper styling for each group

## Quick Example

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

## Command Line Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Generate PDF
python generate_pdf.py workout.prac

# View workout
python parse.py workout.prac
```

## Documentation

- **[Complete Syntax Reference](SYNTAX.md)** - Full syntax documentation
- **[Web App](https://swim-set-writer.streamlit.app)** - Try it online
- **[Examples](examples/)** - Sample workout files

## Development

```bash
# Run web app locally
python -m streamlit run app.py

# Run tests
python tests/run_tests.py
```

## Files

- `app.py` - Streamlit web app
- `parse.py` - Core parsing logic
- `generate_pdf.py` - PDF generation
- `SYNTAX.md` - Complete syntax reference
- `examples/` - Example workout files

---

### Local Development
To run the web app locally:
```bash
pip install streamlit
python -m streamlit run app.py
```

