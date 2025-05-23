from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from chord_composer import ChordComposer
from note_converter import NoteConverter

class ChordWindow(QWidget):
    # Chord finder window UI
    chordComposed = pyqtSignal(str)
    
    def __init__(self, MainWindow):
        super().__init__()
        self.main_window = MainWindow
        self.chord = []
        self.composer = ChordComposer()
        
        # Initialize UI components
        self.label = QLabel("No chord composed yet.")
        
        # Root note combo
        self.rootNoteCombo = QComboBox()
        self.rootNoteCombo.addItems(["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B", "C2"])
        
        self.chordTypeCombo = QComboBox()
        self.chordTypeCombo.addItems(["major", "minor", "diminished"])
        
        # ADD: Connect chord type change to update root note notation
        self.chordTypeCombo.currentTextChanged.connect(self.on_chord_type_changed)
        
        self.composeButton = QPushButton("Compose chord")
        self.composeButton.clicked.connect(self.composeChord)
        
        # Connect signals
        self.composer.chordComposed.connect(self.displayChord)
        self.sendToPianoButton = QPushButton("Send to Piano")
        self.sendToPianoButton.clicked.connect(self.highlightPianoButtons)
        
        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Root note:"))
        layout.addWidget(self.rootNoteCombo)
        layout.addWidget(QLabel("Chord type:"))
        layout.addWidget(self.chordTypeCombo)
        layout.addWidget(self.label)
        layout.addWidget(self.composeButton)
        layout.addWidget(self.sendToPianoButton)
        self.setLayout(layout)

    def on_chord_type_changed(self):
        # Handle chord type change - adjust root note display for diminished chords
        chord_type = self.chordTypeCombo.currentText()
        current_root = self.rootNoteCombo.currentText()
        
        # For diminished chords, convert to flat notation if sharp equivalent is selected
        if chord_type == "diminished":
            # Use NoteConverter to get flat notation
            flat_equivalent = NoteConverter.convert_for_diminished_chord(current_root)
            
            # If conversion happened (it was a sharp note), update the combo box
            if flat_equivalent != current_root:
                index = self.rootNoteCombo.findText(flat_equivalent)
                if index >= 0:
                    self.rootNoteCombo.setCurrentIndex(index)


    # Generate chord based on selected parameters
    def composeChord(self):
        # Get the selected root note
        root_note = self.rootNoteCombo.currentText()
        
        # Add octave number "1" to notes except "C2" which already has it
        if root_note != "C2":
            root = root_note + "4"
        else:
            root = "C5"

        chordType = self.chordTypeCombo.currentText()
        self.composer.composeChord(root, chordType)
        self.sendToPianoButton.setEnabled(True)
    
    # Update UI with composed chord information
    def displayChord(self, chordName, chord):
        # Get current chord type for proper display
        chord_type = self.chordTypeCombo.currentText()
        
        # For diminished chords, ensure chord name uses flat notation
        if chord_type == "diminished":
            # Convert chord notes to flat notation for display
            display_notes = []
            for note in chord:
                note_without_octave = note[:-1] if len(note) > 1 and note[-1].isdigit() else note
                flat_note = NoteConverter.convert_for_diminished_chord(note_without_octave)
                display_notes.append(flat_note)
            display_chord_name = " ".join(display_notes)
        else:
            display_chord_name = chordName
        
        self.label.setText("Chord composed: {}".format(display_chord_name))
        self.chordComposed.emit(display_chord_name)
        self.chord = chord

    # Highlight piano keys one by one for the generated chord
    def highlightPianoButtons(self):
        self.noteIndex = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.playNextNote)
        self.timer.start(50)  # 50ms interval between notes

    # Play each note in the chord sequentially
    def playNextNote(self):
        if self.noteIndex < len(self.chord):
            note = self.chord[self.noteIndex]
            
            # Use NoteConverter for piano button lookup
            piano_note = NoteConverter.convert_for_piano_button(note)
            button = self.main_window.buttons.get(piano_note)
            
            if button:
                button.setStyleSheet("background-color: rgb(255,165,0)")  # Orange highlight
                
                # If octave shift is active, update the display to show adjusted note names
                if self.main_window.octave_shift != 0 and len(note) > 1 and note[-1].isdigit():
                    base_note = note[:-1]
                    original_octave = int(note[-1])
                    new_octave = original_octave + self.main_window.octave_shift
                    adjusted_note = base_note + str(new_octave)
                    
                    # Update the chord label to show octave-shifted notes
                    current_text = self.label.text()
                    if "Chord composed:" in current_text and note in current_text:
                        self.label.setText(current_text.replace(note, adjusted_note))
                
                self.main_window.notes_sound(note, self.main_window.volume, self.main_window.octave_shift)
            self.noteIndex += 1
        else:
            self.timer.stop()
            QTimer.singleShot(3000, self.reset)  # Reset highlights after 3 seconds

    # Reset all highlighted piano keys to their original state
    def reset(self):
        self.main_window.reset_all_piano_highlights()
        
        if hasattr(self, "timer") and self.timer.isActive():
            self.timer.stop()
        self.label.setText("No chord composed yet.")