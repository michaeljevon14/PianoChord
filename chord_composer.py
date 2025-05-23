from PyQt5.QtCore import QObject, pyqtSignal
from note_converter import NoteConverter

class ChordComposer(QObject):
    # Core component that handles chord theory and composition
    
    # Signal emitted when chord is composed
    chordComposed = pyqtSignal(str, object)
    
    def __init__(self):
        super().__init__()
        self.chord = []
    
    def composeChord(self, root, chordType):
        # Compose a chord based on root note and chord type
        # Dictionary of intervals defining chord types
        intervals = {
            "major": [4, 7],       # Major chord: root + major 3rd (4 semitones) + perfect 5th (7 semitones)
            "minor": [3, 7],       # Minor chord: root + minor 3rd (3 semitones) + perfect 5th (7 semitones)
            "diminished": [3, 6]   # Diminished chord: root + minor 3rd (3 semitones) + diminished 5th (6 semitones)
        }
        
        # All possible notes in Western music with correct octave notation - using sharps for piano compatibility
        notes_octave1 = ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4"]
        notes_octave2 = ["C5", "C#5", "D5", "D#5", "E5", "F5", "F#5", "G5", "G#5", "A5", "A#5", "B5", "C6"]
        
        # Combine octaves for a continuous range of notes (all in sharp notation for piano compatibility)
        notes = notes_octave1 + notes_octave2
        
        # Extract root note name and octave
        if len(root) > 1 and root[-1].isdigit():
            root_name = root[:-1]
            root_octave = root[-1]
        else:
            root_name = root
            root_octave = "4"
            root = root + "4"
        
        # For diminished chords, convert root to flat notation for proper display
        # but keep the sharp version for piano button lookup
        original_root = root
        if chordType == "diminished":
            root = NoteConverter.convert_for_diminished_chord(root)
            root_name = root[:-1]

        # Find position of root note in sharp notation (for piano compatibility)
        piano_root = NoteConverter.convert_for_piano_button(original_root)
        try:
            if root_octave == "4":
                root_index = notes_octave1.index(piano_root)
                notes_to_use = notes
            else:
                if piano_root == "C6":
                    root_index = len(notes_octave1) + notes_octave2.index(piano_root)
                else:
                    root_index = len(notes_octave1) + notes_octave2.index(piano_root)
                notes_to_use = notes
        except ValueError:
            print(f"Error: Note '{piano_root}' not found in notes list.")
            # Default to C4 if there's an error
            root = "C4"
            root_index = 0
            notes_to_use = notes
        
        # Generate chord using sharp notation for piano compatibility
        chord = [piano_root]  # Start with the root note in sharp notation
        
        # Calculate chord notes by adding intervals to the root
        for interval in intervals[chordType]:
            index = root_index + interval
            if index < len(notes_to_use):
                chord.append(notes_to_use[index])
            else:
                # Handle overflow to next octave if needed
                next_octave_note = notes_to_use[index % len(notes_to_use)]
                chord.append(next_octave_note)
        
        # For display purposes, convert to appropriate notation
        if chordType == "diminished":
            display_chord = NoteConverter.convert_note_list_for_diminished(chord)
            display_notes = [note[:-1] if len(note) > 1 and note[-1].isdigit() else note for note in display_chord]
        else:
            display_notes = [note[:-1] if len(note) > 1 and note[-1].isdigit() else note for note in chord]
        
        chordName = " ".join(display_notes)
        
        # Store the chord in sharp notation for piano compatibility
        self.chord = chord
        
        # Emit signal with chord information
        self.chordComposed.emit(chordName, self.chord)
        return chordName, chord

    def calculate_progression_chords(self, root, pattern):
        # Convert Roman numeral pattern to actual chord names based on the key
        
        # Extract root note name and octave
        if len(root) > 1 and root[-1].isdigit():
            root_name = root[:-1]
            root_octave = root[-1]
        else:
            root_name = root
            root_octave = "4"
            root = root + root_octave
        
        # All chromatic notes for octave 1 and 2 (sharp notation for piano compatibility)
        notes_octave1 = ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4"]
        notes_octave2 = ["C5", "C#5", "D5", "D#5", "E5", "F5", "F#5", "G5", "G#5", "A5", "A#5", "B5", "C6"]
        
        # Define the scale degrees and their intervals in a major scale
        scale_degrees = {
            "I": 0, "ii": 2, "iii": 4, "IV": 5, "V": 7, "vi": 9, "vii": 11
        }
        
        # Define chord types for each scale degree in major keys
        degree_chord_types = {
            "I": "major", "ii": "minor", "iii": "minor", "IV": "major",
            "V": "major", "vi": "minor", "vii": "diminished"
        }
        
        # Convert root to sharp notation for calculations
        piano_root = NoteConverter.convert_for_piano_button(root)
        
        # Determine which octave array to use based on the root note
        if root_octave == "4":
            notes = notes_octave1
            next_octave_notes = notes_octave2
            root_index = notes.index(piano_root)
        else:
            notes = notes_octave2
            next_octave_notes = ["C6", "C#6", "D6", "D#6", "E6"]
            root_index = notes.index(piano_root)
            
        progression = []
        
        # Calculate each chord in the progression
        for degree in pattern:
            interval = scale_degrees[degree]
            chord_index = (root_index + interval) % 12
            
            # If we need to move to the next octave
            if (root_index + interval) >= 12 and root_octave == "4":
                chord_root = next_octave_notes[chord_index]
            elif (root_index + interval) >= 12 and root_octave == "5":
                chord_root = next_octave_notes[chord_index]
            else:
                chord_root = notes[chord_index]
                
            chord_type = degree_chord_types[degree]

            # For diminished chords in progressions, convert to flat notation for display
            if chord_type == "diminished":
                display_root = NoteConverter.convert_for_diminished_chord(chord_root)
                progression.append((display_root, chord_type))
            else:
                progression.append((chord_root, chord_type))
                
        return progression