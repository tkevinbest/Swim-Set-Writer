import re
from typing import List, Dict, Any, Optional

class WorkoutConfig:
    def __init__(self, units: str = "meters", title: str = None, author: str = None, 
                 date: str = None, description: str = None, level: str = None):
        self.units = units.lower()
        if self.units not in ["meters", "yards", "m", "y"]:
            raise ValueError(f"Invalid units: {units}. Must be 'meters', 'yards', 'm', or 'y'")
        
        # Normalize units
        if self.units in ["meters", "m"]:
            self.units = "meters"
            self.unit_symbol = "m"
        else:
            self.units = "yards"
            self.unit_symbol = "y"
        
        # Metadata fields
        self.title = title
        self.author = author
        self.date = date
        self.description = description
        self.level = level

class PracticeSet:
    def __init__(self, name: str, repeat: int = 1, items: Optional[List['SetItem']] = None):
        self.name = name
        self.repeat = repeat
        self.items = items or []
    
    def total_distance(self, group: str = 'A') -> int:
        """Calculate total distance for this set including repetitions"""
        set_distance = sum(item.total_distance(group) for item in self.items)
        return set_distance * self.repeat
    
    def get_available_groups(self) -> List[str]:
        """Get all groups available in this set"""
        all_groups = set(['A'])
        for item in self.items:
            all_groups.update(item.get_available_groups())
        return sorted(list(all_groups))
    
    def __str__(self) -> str:
        return f"{self.name} (x{self.repeat}): {self.total_distance()}m total"

class GroupVariation:
    """Represents a workout variation for a specific group"""
    def __init__(self, reps: int, distance: int, desc: str, intervals: List[str]):
        self.reps = reps
        self.distance = distance
        self.desc = desc
        self.intervals = intervals
    
    def total_distance(self) -> int:
        return self.reps * self.distance

class SetItem:
    def __init__(self, reps: int, distance: int, desc: str, intervals: List[str], 
                 note: Optional[str] = None, group_variations: Optional[Dict[str, GroupVariation]] = None):
        # Primary workout (A group by default)
        self.reps = reps
        self.distance = distance
        self.desc = desc
        self.intervals = intervals
        self.note = note
        
        # Group-specific variations (B, C, etc.)
        self.group_variations = group_variations or {}
    
    def get_variation_for_group(self, group: str) -> GroupVariation:
        """Get the workout variation for a specific group"""
        if group.upper() == 'A' or group not in self.group_variations:
            # Return A group (default) variation
            return GroupVariation(self.reps, self.distance, self.desc, self.intervals)
        else:
            return self.group_variations[group]
    
    def total_distance(self, group: str = 'A') -> int:
        """Calculate total distance for this item for a specific group"""
        variation = self.get_variation_for_group(group)
        return variation.total_distance()
    
    def get_available_groups(self) -> List[str]:
        """Get list of all available groups for this item"""
        groups = ['A']
        groups.extend(self.group_variations.keys())
        return sorted(groups)
    
    def __str__(self) -> str:
        interval_str = f" @ {'/'.join(self.intervals)}" if self.intervals else ""
        note_str = f" # {self.note}" if self.note else ""
        rep_str = f"{self.reps}x" if self.reps > 1 else ""
        
        # Add group variations if any
        variation_str = ""
        if self.group_variations:
            for group, variation in self.group_variations.items():
                var_rep_str = f"{variation.reps}x" if variation.reps > 1 else ""
                var_interval_str = f" @ {'/'.join(variation.intervals)}" if variation.intervals else ""
                variation_str += f" [{var_rep_str}{variation.distance} {variation.desc}{var_interval_str}]"
        
        return f"  {rep_str}{self.distance} {self.desc}{interval_str}{variation_str}{note_str}"

def parse_prac(filename: str) -> tuple[WorkoutConfig, List[PracticeSet]]:
    """Parse a .prac file and return configuration and list of PracticeSet objects"""
    sets = []
    current_set = None
    
    # Metadata/config storage
    metadata = {}
    config_section_ended = False
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Practice file '{filename}' not found")
    except Exception as e:
        raise Exception(f"Error reading file '{filename}': {e}")
    
    for line_num, line in enumerate(lines, start=1):
        original_line = line.rstrip('\n')
        
        # Handle comments - extract note if at end of line
        comment_match = re.search(r'#(.*)$', original_line)
        note = comment_match.group(1).strip() if comment_match else None
        
        # Remove comments for parsing
        line_content = re.split(r'#', original_line, maxsplit=1)[0].strip()
        
        # Skip empty lines
        if not line_content:
            continue

        # Configuration/metadata lines (only at the beginning, before any sets)
        if not config_section_ended and not sets:
            # Match any key: value pair
            config_match = re.match(r'^(\w+):\s*(.+)\s*$', line_content)
            if config_match:
                key = config_match.group(1).lower()
                value = config_match.group(2).strip()
                
                # Validate known metadata fields
                valid_fields = ['units', 'title', 'author', 'date', 'description', 'level']
                if key in valid_fields:
                    metadata[key] = value
                    continue
                else:
                    print(f"Warning: Unknown metadata field '{key}' on line {line_num}")
                    continue
            else:
                # No more config lines, mark config section as ended
                config_section_ended = True

        # Header line: "Main Set x2:" or "Warmup:"
        header_match = re.match(r'^(.+?)(?: x(\d+))?:$', line_content)
        if header_match:
            set_name = header_match.group(1).strip()
            set_repeat = int(header_match.group(2)) if header_match.group(2) else 1
            current_set = PracticeSet(name=set_name, repeat=set_repeat)
            sets.append(current_set)
            continue

        # Indented item line (must belong to current_set)
        if original_line.startswith(' ') or original_line.startswith('\t'):
            if current_set is None:
                raise ValueError(f"Line {line_num}: Item found outside of any set:\n{original_line}")
            
            item_line = line_content.strip()
            
            # Parse line with potential group variations
            # Format: "3x50 kick @ :55/1:10 [2x75 kick @ 1:20]"
            
            # First, extract any group variations in brackets
            group_variations = {}
            
            # Find and extract bracket content
            bracket_pattern = r'\[([^\]]+)\]'
            bracket_matches = re.findall(bracket_pattern, item_line)
            
            # Remove brackets from the main line
            main_line = re.sub(bracket_pattern, '', item_line).strip()
            
            # Parse main workout (A group)
            item_match = re.match(r'(?:(\d+)x)?(\d+)\s+([^@]+?)(?:\s*@\s*(.+))?$', main_line)
            
            if item_match:
                reps = int(item_match.group(1)) if item_match.group(1) else 1
                distance = int(item_match.group(2))
                desc = item_match.group(3).strip()
                intervals = []
                if item_match.group(4):
                    intervals = [iv.strip() for iv in item_match.group(4).split('/')]
                
                # Validate main workout data
                if distance <= 0:
                    raise ValueError(f"Line {line_num}: Distance must be positive: {distance}")
                if reps <= 0:
                    raise ValueError(f"Line {line_num}: Repetitions must be positive: {reps}")
                if not desc:
                    raise ValueError(f"Line {line_num}: Description cannot be empty")
                if intervals and not validate_intervals(intervals):
                    raise ValueError(f"Line {line_num}: Invalid interval format. Use MM:SS or H:MM:SS format.")
                
                # Parse group variations (currently only support B group)
                if bracket_matches:
                    for i, bracket_content in enumerate(bracket_matches):
                        group_name = chr(ord('B') + i)  # B, C, D, etc.
                        
                        var_match = re.match(r'(?:(\d+)x)?(\d+)\s+([^@]+?)(?:\s*@\s*(.+))?$', bracket_content.strip())
                        if var_match:
                            var_reps = int(var_match.group(1)) if var_match.group(1) else 1
                            var_distance = int(var_match.group(2))
                            var_desc = var_match.group(3).strip()
                            var_intervals = []
                            if var_match.group(4):
                                var_intervals = [iv.strip() for iv in var_match.group(4).split('/')]
                            
                            # Validate variation data
                            if var_distance <= 0:
                                raise ValueError(f"Line {line_num}: Group {group_name} distance must be positive: {var_distance}")
                            if var_reps <= 0:
                                raise ValueError(f"Line {line_num}: Group {group_name} repetitions must be positive: {var_reps}")
                            if not var_desc:
                                raise ValueError(f"Line {line_num}: Group {group_name} description cannot be empty")
                            if var_intervals and not validate_intervals(var_intervals):
                                raise ValueError(f"Line {line_num}: Group {group_name} invalid interval format.")
                            
                            group_variations[group_name] = GroupVariation(var_reps, var_distance, var_desc, var_intervals)
                
                item = SetItem(reps, distance, desc, intervals, note, group_variations)
                current_set.items.append(item)
            else:
                raise ValueError(f"Line {line_num}: Could not parse item line:\n{original_line}")
        else:
            # Non-indented, non-header line - might be an error
            if line_content.strip():  # Not empty
                print(f"Warning: Line {line_num} ignored (not indented, not a header): {original_line}")

    # Create config object with parsed metadata
    config = WorkoutConfig(
        units=metadata.get('units', 'meters'),
        title=metadata.get('title'),
        author=metadata.get('author'),
        date=metadata.get('date'),
        description=metadata.get('description'),
        level=metadata.get('level')
    )
    
    return config, sets

class WorkoutSummary:
    """Class to handle workout analysis and formatting"""
    
    def __init__(self, config: WorkoutConfig, sets: List[PracticeSet]):
        self.config = config
        self.sets = sets
    
    def get_all_groups(self) -> List[str]:
        """Get all groups present in the workout"""
        all_groups = set(['A'])
        for set_ in self.sets:
            all_groups.update(set_.get_available_groups())
        return sorted(list(all_groups))
    
    def total_distance(self, group: str = 'A') -> int:
        """Calculate total workout distance for a specific group"""
        return sum(set_.total_distance(group) for set_ in self.sets)
    
    def format_workout(self, group: str = None) -> str:
        """Format the workout for display, optionally for a specific group"""
        if group is None:
            # Show combined view
            return self._format_combined_workout()
        else:
            # Show group-specific view
            return self._format_group_workout(group)
    
    def _format_combined_workout(self) -> str:
        """Format workout showing all groups together (legacy format)"""
        lines = []
        lines.append("=" * 50)
        
        # Title (use from metadata or default)
        title = self.config.title or "SWIM WORKOUT"
        lines.append(title.upper())
        
        # Metadata info
        if self.config.author:
            lines.append(f"Coach: {self.config.author}")
        if self.config.date:
            lines.append(f"Date: {self.config.date}")
        if self.config.level:
            lines.append(f"Level: {self.config.level}")
        if self.config.description:
            lines.append(f"Description: {self.config.description}")
        
        lines.append(f"Units: {self.config.units.title()}")
        lines.append("=" * 50)
        
        for set_ in self.sets:
            lines.append(f"\n{set_.name.upper()}" + (f" x{set_.repeat}" if set_.repeat > 1 else ""))
            lines.append("-" * 30)
            
            for item in set_.items:
                lines.append(str(item))
            
            lines.append(f"Set Total: {set_.total_distance()}{self.config.unit_symbol}")
        
        lines.append("=" * 50)
        lines.append(f"WORKOUT TOTAL: {self.total_distance()}{self.config.unit_symbol}")
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    def _format_group_workout(self, group: str) -> str:
        """Format workout for a specific group"""
        lines = []
        lines.append("=" * 50)
        
        # Title with group specification
        title = self.config.title or "SWIM WORKOUT"
        lines.append(f"{title.upper()} - GROUP {group.upper()}")
        
        # Metadata info
        if self.config.author:
            lines.append(f"Coach: {self.config.author}")
        if self.config.date:
            lines.append(f"Date: {self.config.date}")
        if self.config.level:
            lines.append(f"Level: {self.config.level}")
        if self.config.description:
            lines.append(f"Description: {self.config.description}")
        
        lines.append(f"Units: {self.config.units.title()}")
        lines.append("=" * 50)
        
        for set_ in self.sets:
            lines.append(f"\n{set_.name.upper()}" + (f" x{set_.repeat}" if set_.repeat > 1 else ""))
            lines.append("-" * 30)
            
            for item in set_.items:
                variation = item.get_variation_for_group(group)
                interval_str = f" @ {'/'.join(variation.intervals)}" if variation.intervals else ""
                note_str = f" # {item.note}" if item.note else ""
                rep_str = f"{variation.reps}x" if variation.reps > 1 else ""
                lines.append(f"  {rep_str}{variation.distance} {variation.desc}{interval_str}{note_str}")
            
            lines.append(f"Set Total: {set_.total_distance(group)}{self.config.unit_symbol}")
        
        lines.append("=" * 50)
        lines.append(f"WORKOUT TOTAL: {self.total_distance(group)}{self.config.unit_symbol}")
        lines.append("=" * 50)
        
        return "\n".join(lines)

def validate_intervals(intervals: List[str]) -> bool:
    """Validate that intervals are in correct time format"""
    for interval in intervals:
        # Allow formats like: :30, 1:00, 1:30, 12:00, etc.
        # Format 1: :SS (where SS is 00-59)
        if re.match(r'^:[0-5]\d$', interval):
            seconds = int(interval[1:])
            if seconds <= 59:
                continue
        # Format 2: MM:SS (where MM is 0-59, SS is 00-59)  
        elif re.match(r'^([0-5]?\d):[0-5]\d$', interval):
            parts = interval.split(':')
            minutes = int(parts[0])
            seconds = int(parts[1])
            if minutes <= 59 and seconds <= 59:
                continue
        # Format 3: H:MM:SS or HH:MM:SS
        elif re.match(r'^\d+:[0-5]\d:[0-5]\d$', interval):
            parts = interval.split(':')
            if len(parts) == 3:
                minutes = int(parts[1])
                seconds = int(parts[2])
                if minutes <= 59 and seconds <= 59:
                    continue
        
        # If we get here, the interval is invalid
        return False
    
    return True

# Example usage
if __name__ == "__main__":
    import sys
    
    filename = "example_set.prac"
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    
    try:
        config, sets = parse_prac(filename)
        workout = WorkoutSummary(config, sets)
        
        # Show all available groups
        all_groups = workout.get_all_groups()
        
        if len(all_groups) == 1:
            # Only one group, show normal format
            print(workout.format_workout())
        else:
            # Multiple groups, show each group separately
            for group in all_groups:
                if group != all_groups[0]:
                    print("\n" + "="*60 + "\n")
                print(workout.format_workout(group))
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)