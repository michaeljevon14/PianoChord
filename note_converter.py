class NoteConverter:
    """
    Unified note conversion system for the Piano Chord Learning App.
    Handles all note conversions between sharp and flat notation,
    specifically for diminished chords and piano button mapping.
    """
    
    # Sharp to flat conversion mapping (for diminished chords)
    SHARP_TO_FLAT = {
        "C#": "Db", "D#": "Eb", "F#": "Gb", "G#": "Ab", "A#": "Bb"
    }
    
    # Flat to sharp conversion mapping (for piano button lookup)
    FLAT_TO_SHARP = {
        "Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"
    }
    
    @staticmethod
    def to_flat_notation(note):
        """
        Convert sharp notation to flat notation for diminished chords.
        Handles notes with or without octave numbers.
        
        Args:
            note (str): Note name (e.g., "C#4", "F#", "Db5")
            
        Returns:
            str: Note in flat notation (e.g., "Db4", "Gb", "Db5")
        """
        if not note:
            return note
            
        # Extract base note and octave
        if len(note) > 1 and note[-1].isdigit():
            base_note = note[:-1]
            octave = note[-1]
        else:
            base_note = note
            octave = ""
        
        # Convert if it's a sharp note, otherwise keep original
        flat_note = NoteConverter.SHARP_TO_FLAT.get(base_note, base_note)
        return flat_note + octave
    
    @staticmethod
    def to_sharp_notation(note):
        """
        Convert flat notation to sharp notation for piano button lookup.
        Handles notes with or without octave numbers.
        
        Args:
            note (str): Note name (e.g., "Db4", "Gb", "C#5")
            
        Returns:
            str: Note in sharp notation (e.g., "C#4", "F#", "C#5")
        """
        if not note:
            return note
            
        # Extract base note and octave
        if len(note) > 1 and note[-1].isdigit():
            base_note = note[:-1]
            octave = note[-1]
        else:
            base_note = note
            octave = ""
        
        # Convert if it's a flat note, otherwise keep original
        sharp_note = NoteConverter.FLAT_TO_SHARP.get(base_note, base_note)
        return sharp_note + octave
    
    @staticmethod
    def convert_for_diminished_chord(note):
        """
        Specifically convert notes for diminished chord notation.
        This is an alias for to_flat_notation for clarity.
        
        Args:
            note (str): Note name
            
        Returns:
            str: Note in appropriate notation for diminished chord
        """
        return NoteConverter.to_flat_notation(note)
    
    @staticmethod
    def convert_for_piano_button(note):
        """
        Convert notes for piano button lookup (piano uses sharp notation).
        This is an alias for to_sharp_notation for clarity.
        
        Args:
            note (str): Note name
            
        Returns:
            str: Note in sharp notation for piano button lookup
        """
        return NoteConverter.to_sharp_notation(note)
    
    @staticmethod
    def convert_note_list_for_diminished(notes):
        """
        Convert a list of notes to flat notation for diminished chords.
        
        Args:
            notes (list): List of note names
            
        Returns:
            list: List of notes in flat notation
        """
        return [NoteConverter.to_flat_notation(note) for note in notes]
    
    @staticmethod
    def convert_note_list_for_piano(notes):
        """
        Convert a list of notes to sharp notation for piano button lookup.
        
        Args:
            notes (list): List of note names
            
        Returns:
            list: List of notes in sharp notation
        """
        return [NoteConverter.to_sharp_notation(note) for note in notes]
    
    @staticmethod
    def is_enharmonic_equivalent(note1, note2):
        """
        Check if two notes are enharmonic equivalents (same pitch, different notation).
        
        Args:
            note1 (str): First note name
            note2 (str): Second note name
            
        Returns:
            bool: True if notes are enharmonic equivalents
        """
        # Convert both to sharp notation for comparison
        sharp1 = NoteConverter.to_sharp_notation(note1)
        sharp2 = NoteConverter.to_sharp_notation(note2)
        return sharp1 == sharp2
    
    @staticmethod
    def get_display_name(note, chord_type=None):
        """
        Get the appropriate display name for a note based on chord type.
        
        Args:
            note (str): Note name with octave
            chord_type (str): Type of chord ("diminished", "major", "minor")
            
        Returns:
            str: Note name without octave in appropriate notation
        """
        # Remove octave number for display
        if len(note) > 1 and note[-1].isdigit():
            base_note = note[:-1]
        else:
            base_note = note
        
        # For diminished chords, use flat notation
        if chord_type == "diminished":
            return NoteConverter.to_flat_notation(base_note)
        else:
            return base_note