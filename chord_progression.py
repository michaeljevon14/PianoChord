from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from chord_composer import ChordComposer

class ChordProgressionWindow(QWidget):
    # Chord progression window - For playing sequences of related chords
    def __init__(self, MainWindow):
        super().__init__()
        self.main_window = MainWindow
        self.setWindowTitle("Chord Progression")
        self.resize(400, 300)
        
        # Initialize variables
        self.root_chord = None
        self.progression_chords = []
        self.current_chord_index = 0
        
        # UI Setup
        layout = QVBoxLayout()
        
        # Selected root chord display
        self.root_display = QLabel("No root chord selected")
        self.root_display.setAlignment(Qt.AlignCenter)
        self.root_display.setStyleSheet("border:1px solid black; background-color: #f0f0f0; padding: 5px;")
        
        # Progression selection dropdown
        self.progression_group = QGroupBox("Progression Type")
        progression_layout = QVBoxLayout()
        self.progression_combo = QComboBox()
        
        # Available chord progressions
        self.progression_combo.addItems([
            "I-V-vi-IV",
            "I-IV-V-V",
            "ii-V-I-vi",
            "I-vi-IV-V",
            "I-iii-vi-IV",
            "I-V-vi-iii-IV-I-IV-V"
        ])
        
        progression_layout.addWidget(self.progression_combo)
        self.progression_group.setLayout(progression_layout)
        
        # Generated progression display
        self.progression_display = QLabel("No progression generated yet")
        self.progression_display.setAlignment(Qt.AlignCenter)
        self.progression_display.setStyleSheet("border:1px solid black; min-height: 50px; background-color: white;")
        
        # Notes display area
        self.notes_display = QLabel("Notes: ")
        self.notes_display.setAlignment(Qt.AlignCenter)
        self.notes_display.setStyleSheet("border:1px solid black; min-height: 30px; background-color: white;")
        layout.addWidget(QLabel("Notes:"))
        layout.addWidget(self.notes_display)

        # Control buttons
        button_layout = QHBoxLayout()
        
        self.generate_button = QPushButton("Generate Progression")
        self.generate_button.setEnabled(False)  # Disabled until root chord is selected
        self.generate_button.clicked.connect(self.generate_progression)
        
        self.play_button = QPushButton("Play Progression")
        self.play_button.setEnabled(False)  # Disabled until progression is generated
        self.play_button.clicked.connect(self.play_progression)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)  # Disabled until progression is playing
        self.stop_button.clicked.connect(self.stop_progression)
        
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.stop_button)

        # Loop checkbox
        self.loop_checkbox = QCheckBox("Loop Progression")
        self.loop_checkbox.setChecked(False)  # Default to not looping
        
        # Add all components to main layout
        layout.addWidget(QLabel("Root Chord:"))
        layout.addWidget(self.root_display)
        layout.addWidget(self.progression_group)
        layout.addWidget(QLabel("Generated Progression:"))
        layout.addWidget(self.progression_display)
        layout.addWidget(self.loop_checkbox)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    # Set the root chord from the chord composer
    def set_root_chord(self, root, chord_type):
        self.root_chord = (root, chord_type)
        display_root = root[:-1] if len(root) > 1 and root[-1].isdigit() else root
        self.root_display.setText(f"Root: {display_root} {chord_type}")
        self.generate_button.setEnabled(True)
    
    # Generate chord progression based on root chord and selected progression type
    def generate_progression(self):
        if not self.root_chord:
            return
            
        root, chord_type = self.root_chord
        progression_type = self.progression_combo.currentText()
        
        # Define progression patterns using Roman numerals
        progression_patterns = {
            "I-V-vi-IV": ["I", "V", "vi", "IV"],
            "I-IV-V-V": ["I", "IV", "V", "V"],
            "ii-V-I-vi": ["ii", "V", "I", "vi"],
            "I-vi-IV-V": ["I", "vi", "IV", "V"],
            "I-iii-vi-IV": ["I", "iii", "vi", "IV"],
            "I-V-vi-iii-IV-I-IV-V": ["I", "V", "vi", "iii", "IV", "I", "IV", "V"]
        }
        
        pattern = progression_patterns[progression_type]
        
        # Calculate actual chords based on the pattern and root
        composer = ChordComposer()
        self.progression_chords = composer.calculate_progression_chords(root, pattern)
        
        # Update the display
        progression_text = " → ".join([f"{chord[0][:-1] if len(chord[0]) > 1 and chord[0][-1].isdigit() else chord[0]} {chord[1]}" for chord in self.progression_chords])
        self.progression_display.setText(progression_text)
        self.play_button.setEnabled(True)

    # Adjust note names based on current octave shift
    def adjust_notes_for_octave_shift(self, chord_notes):
        # Adjust chord note names to reflect the current octave shift
        adjusted_notes = []
        for note in chord_notes:
            if len(note) > 1 and note[-1].isdigit():
                base_note = note[:-1]
                original_octave = int(note[-1])
                new_octave = original_octave + self.main_window.octave_shift
                adjusted_notes.append(base_note + str(new_octave))
            else:
                adjusted_notes.append(note)
        return adjusted_notes

    # Play the generated chord progression
    def play_progression(self):
        if not self.progression_chords:
            return
            
        self.current_chord_index = 0
        self.play_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        # Get loop setting from checkbox
        self.is_looping = self.loop_checkbox.isChecked()
        
        # Start timer to play chords sequentially
        self.play_timer = QTimer()
        self.play_timer.timeout.connect(self.play_next_chord)
        self.play_timer.start(1500)  # 1.5 seconds per chord
        
        # Play the first chord immediately
        self.play_next_chord()
    
    # Play each chord in the progression sequence
    def play_next_chord(self):
        # Check if we've played all chords
        if self.current_chord_index >= len(self.progression_chords):
            # If looping is enabled, reset to the beginning
            if self.is_looping:
                self.current_chord_index = 0
            else:
                self.stop_progression()
                return
            
        # Reset previous chord highlights
        self.reset_highlights()
        
        # Get current chord
        current_chord = self.progression_chords[self.current_chord_index]
        root, chord_type = current_chord
        
        # Use chord composer to get the notes
        composer = ChordComposer()
        _, chord_notes = composer.composeChord(root, chord_type)
        
        # Store the current chord info for octave updates
        self.last_played_chord_notes = chord_notes
        self.last_played_chord_info = (root, chord_type)

        # Adjust notes for current octave shift and update display
        adjusted_notes = self.adjust_notes_for_octave_shift(chord_notes)
        display_notes = [note[:-1] if len(note) > 1 and note[-1].isdigit() else note for note in adjusted_notes]
        self.notes_display.setText("Notes: " + " ".join(display_notes))

        # Update the main window's note label with octave-adjusted notes
        chord_notes_text = " ".join(adjusted_notes)
        display_root = root[:-1] if len(root) > 1 and root[-1].isdigit() else root
        self.main_window.notelabel.setText(f"{display_root} {chord_type}: {chord_notes_text}")

        # Update progression display to show current chord with octave adjustment
        if len(root) > 1 and root[-1].isdigit():
            base_note = root[:-1]
            original_octave = int(root[-1])
            adjusted_octave = original_octave + self.main_window.octave_shift
            display_root_with_octave = f"{base_note}{adjusted_octave}"
        else:
            display_root_with_octave = root
        
        progression_status = f"Playing: {display_root_with_octave} {chord_type} ({self.current_chord_index + 1}/{len(self.progression_chords)})"
        if self.is_looping:
            progression_status += " (Looping)"
        self.progression_display.setText(progression_status)
        
        # Play all notes simultaneously
        self.play_chord_simultaneously(chord_notes)
        
        self.current_chord_index += 1

    # Play all notes in a chord at once
    def play_chord_simultaneously(self, chord_notes):
        for note in chord_notes:
            button = self.main_window.buttons.get(note)
            if button:
                button.setStyleSheet("background-color: rgb(0, 100, 255)")  # Blue highlight
                
                # Get the base note and octave
                if len(note) > 1 and note[-1].isdigit():
                    base_note = note[:-1]
                    original_octave = int(note[-1])
                    
                    # Apply the octave shift
                    new_octave = original_octave + self.main_window.octave_shift
                    
                    # Create adjusted note name for display
                    adjusted_note = base_note + str(new_octave)
                    
                    # Display the adjusted note if octave shift is in effect
                    if self.main_window.octave_shift != 0:
                        # Update the notes display with octave-shifted note names
                        current_text = self.notes_display.text()
                        if note in current_text:
                            self.notes_display.setText(current_text.replace(note, adjusted_note))
                
                # Play the sound with the current octave shift
                self.main_window.notes_sound(note, self.main_window.volume, self.main_window.octave_shift)

    # Update display when octave changes (called from main window)
    def update_octave_display(self):
        # Update the notes display when octave shift changes
        if hasattr(self, 'last_played_chord_notes') and self.last_played_chord_notes:
            adjusted_notes = self.adjust_notes_for_octave_shift(self.last_played_chord_notes)
            display_notes = [note[:-1] if len(note) > 1 and note[-1].isdigit() else note for note in adjusted_notes]
            self.notes_display.setText("Notes: " + " ".join(display_notes))
            
        # Update main window label
        if hasattr(self, 'last_played_chord_info'):
            root, chord_type = self.last_played_chord_info
            display_root = root[:-1] if len(root) > 1 and root[-1].isdigit() else root
            chord_notes_text = " ".join(adjusted_notes)
            self.main_window.notelabel.setText(f"{display_root} {chord_type}: {chord_notes_text}")

    # Reset all piano key highlights
    def reset_highlights(self):
        self.main_window.reset_all_piano_highlights()
    
    # Stop progression playback
    def stop_progression(self):
        if hasattr(self, 'play_timer') and self.play_timer.isActive():
            self.play_timer.stop()
        
        # Reset looping flag
        self.is_looping = False
        
        self.reset_highlights()
        self.play_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # Restore the progression display
        progression_text = " → ".join([f"{chord[0]} {chord[1]}" for chord in self.progression_chords])
        self.progression_display.setText(progression_text)
        self.notes_display.setText("Notes: ")  # Clear the notes display

        # Reset the main window's note label
        self.main_window.notelabel.setText("No chord selected")

    def closeEvent(self, event):
        # Handle window close event
        # Clear the main window's status bar and note label
        self.main_window.mw.statusBar().clearMessage()
        self.main_window.notelabel.setText("No chord selected")
        
        # Stop any active progression
        if hasattr(self, 'play_timer') and self.play_timer.isActive():
            self.play_timer.stop()
        
        # Reset piano highlights
        self.reset_highlights()
        
        # Accept the close event
        event.accept()