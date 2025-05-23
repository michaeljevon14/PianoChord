import fluidsynth
from PyQt5.QtCore import QTimer

class SoundEngine:
    def __init__(self):
        # Initialize the FluidSynth sound engine
        self.fs = fluidsynth.Synth()
        self.fs.start(driver="dsound")  # DirectSound driver for Windows
        self.sfid = self.fs.sfload("Sounds/FluidR3_GM.sf2")  # Load SoundFont
        self.fs.program_select(0, self.sfid, 0, 0)  # Select piano instrument
    
    def play_note(self, note, volume, octave):
        # Play a note with the specified volume and octave
        midi_note = self.note_to_midi(note)
        if midi_note is not None:
            # Apply octave shift - each octave is 12 semitones
            midi_note += (octave * 12)
            # Ensure within MIDI note range (0-127)
            midi_note = max(0, min(127, midi_note))
            
            # Convert volume from 0-100 range to 0-127 range for MIDI
            midi_volume = min(int(volume * 1.27), 127)
            
            # Schedule automatic note-off after shorter duration
            QTimer.singleShot(500, lambda: self.fs.noteoff(0, midi_note))

            # Play the note
            self.fs.noteon(0, midi_note, midi_volume)
            return midi_note
        return None
        
    def note_to_midi(self, note):
        # Convert note name (like 'C4', 'F#3', 'A-1') to MIDI note number
        try:
            # Handle negative octaves (like C-1)
            if note.endswith('-1'):
                note_name = note[:-2]
                octave_num = -1
            elif len(note) > 1 and note[-1].isdigit():
                note_name = note[:-1]
                octave_num = int(note[-1])
            else:
                return None
            
            # Map note names to semitones (C = 0, C# = 1, etc.)
            # Updated to handle both sharp and flat notation
            note_to_semitone = {
                "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, 
                "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
            }
            
            if note_name not in note_to_semitone:
                return None
            
            # Calculate MIDI note number
            # Formula: MIDI = (octave + 1) * 12 + semitone
            # This makes C4 = 60 (middle C)
            midi_note = (octave_num + 1) * 12 + note_to_semitone[note_name]
            
            return midi_note
            
        except (ValueError, IndexError):
            return None
    
    def play_success_sound(self, volume):
        # Play a major chord arpeggio going up (C-E-G-C) for correct answer
        success_notes = [60, 64, 67, 72]  # C4, E4, G4, C5 in MIDI
        
        for i, midi_note in enumerate(success_notes):
            # Convert volume from 0-100 to 0-127 for MIDI
            midi_volume = min(int(volume * 1.27), 127)
            
            # Play each note with a slight delay to create an arpeggio effect
            QTimer.singleShot(i * 270, lambda note=midi_note, vol=midi_volume: self.fs.noteon(0, note, vol))
            # Stop each note after a short duration
            QTimer.singleShot(i * 270 + 200, lambda note=midi_note: self.fs.noteoff(0, note))

    def play_error_sound(self, volume):
        # Play a descending minor pattern (F-D-Bb) for wrong answer
        error_notes = [65, 62, 58]  # F4, D4, Bb3 in MIDI
        
        for i, midi_note in enumerate(error_notes):
            # Convert volume from 0-100 to 0-127 for MIDI
            midi_volume = min(int(volume * 1.27), 127)
            
            # Play each note with a slight delay
            QTimer.singleShot(i * 150, lambda note=midi_note, vol=midi_volume: self.fs.noteon(0, note, vol))
            # Stop each note after a short duration
            QTimer.singleShot(i * 150 + 250, lambda note=midi_note: self.fs.noteoff(0, note))

    def stop_note(self, midi_note):
        # Stop a currently playing note
        self.fs.noteoff(0, midi_note)
    
    def cleanup(self):
        # Clean up FluidSynth resources
        self.fs.delete()