import pygame
import functools
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from sound_engine import SoundEngine
from chord_window import ChordWindow
from chord_progression import ChordProgressionWindow

class Ui_MainWindow(object):
    # Main UI class for Piano Chord Learning App
    
    def __init__(self):
        # Initialize the main window
        # ========== Core Settings ==========
        self.sound_engine = SoundEngine()
        self.fs = self.sound_engine.fs  # For compatibility with existing code
        
        # UI State
        self.learning_mode_active = False
        self.learning_ui = None
        
        # Audio Settings
        self.volume = 50
        self.octave_shift = 0
        
        # Data Storage
        self.chordNotes = []  # To store currently played chord notes
        self.buttons = {}     # Piano button storage
        
        # Octave mapping
        self.octave_names = {
            0: "Sub-contra", 1: "Contra", 2: "Great", 3: "Small", 4: "One-lined",
            5: "Two-lined", 6: "Three-lined", 7: "Four-lined", 8: "Five-lined", 9: "Six-lined"
        }

    # Main UI Setup Methods
    
    def setupUi(self, MainWindow):
        # Setup the main UI with organized sections
        self.mw = MainWindow
        
        # Main Window Setup
        self._setup_main_window()
        
        # UI Sections
        self._setup_piano_keyboard()
        self._setup_volume_controls()
        self._setup_note_display()
        self._setup_octave_controls()
        self._setup_control_buttons()
        self._setup_status_bar()
        
        # Finalizations
        self._connect_signals()
        self._finalize_setup()

    def _setup_main_window(self):
        # Setup main window properties
        self.mw.setObjectName("MainWindow")
        self.mw.resize(640, 400)
        
        # Central widget setup
        self.centralwidget = QWidget(self.mw)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("background-color: white;")
        self.mw.setCentralWidget(self.centralwidget)

    def _setup_piano_keyboard(self):
        # Setup the piano keyboard section
        self._create_piano_buttons()
        self._apply_piano_styling()

    def _setup_volume_controls(self):
        # Setup volume control section
        # Vertical volume slider (left side)
        self.volumeSlider = QtWidgets.QSlider(self.centralwidget)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setValue(self.volume)
        self.volumeSlider.setGeometry(QRect(10, 260, 25, 100))
        self.volumeSlider.setOrientation(Qt.Vertical)
        self.volumeSlider.setTickPosition(QSlider.TicksLeft)
        self.volumeSlider.setTickInterval(25)
        self.volumeSlider.setStyleSheet("QSlider::tick { background: red; }")
        
        # Volume label (above slider)
        self.volumeName = QLabel("Vol", self.centralwidget)
        self.volumeName.setGeometry(QRect(7, 240, 30, 15))
        self.volumeName.setAlignment(Qt.AlignCenter)
        
        # Volume value label (below slider)
        self.volumeValueLabel = QLabel(f"{self.volume}", self.centralwidget)
        self.volumeValueLabel.setGeometry(QRect(7, 365, 30, 15))
        self.volumeValueLabel.setAlignment(Qt.AlignCenter)
        self.volumeValueLabel.setStyleSheet("font-size: 10px;")

    def _setup_note_display(self):
        # Setup note display section
        self.notelabel = QtWidgets.QLabel(self.centralwidget)
        self.notelabel.setStyleSheet('''
            border: 2px solid #515251;
            border-radius: 4px;
            padding: 4px;
        ''')
        self.notelabel.setAlignment(Qt.AlignCenter)
        self.notelabel.setText("No chord selected")
        
        # Center the label
        label_width, label_height = 280, 30
        x_position = (640 - label_width) // 2
        self.notelabel.setGeometry(QRect(x_position, 230, label_width, label_height))

    def _setup_octave_controls(self):
        # Setup octave control section
        # Create octave control frame to contain all octave widgets
        self.octaveControlFrame = QFrame(self.centralwidget)
        self.octaveControlFrame.setGeometry(QRect(60, 240, 40, 140))

        # Create vertical layout for the frame
        octave_layout = QVBoxLayout(self.octaveControlFrame)
        octave_layout.setContentsMargins(2, 0, 2, 0)
        octave_layout.setSpacing(8)

        # Octave label (above controls)
        self.octaveLabel = QLabel("Octave")
        self.octaveLabel.setGeometry(QRect(60, 240, 35, 15))
        self.octaveLabel.setAlignment(Qt.AlignCenter)

        # Octave increase button (top)
        self.highOctaveButton = QPushButton("+")
        self.highOctaveButton.setFixedSize(30, 30)
        self.highOctaveButton.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 3px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        
        # Octave display label (middle)
        self.octaveDisplayLabel = QLabel(f"{self.octave_shift}")
        self.octaveDisplayLabel.setFixedSize(30, 45)
        self.octaveDisplayLabel.setAlignment(Qt.AlignCenter)
        self.octaveDisplayLabel.setStyleSheet("""
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 3px;
            font-weight: bold;
            font-size: 11px;
            color: #333;
        """)
        
        # Octave decrease button (bottom)
        self.lowOctaveButton = QPushButton("-")
        self.lowOctaveButton.setFixedSize(30, 30)
        self.lowOctaveButton.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 3px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)

        # Add controls to layout
        octave_layout.addWidget(self.octaveLabel)
        octave_layout.addWidget(self.highOctaveButton)
        octave_layout.addWidget(self.octaveDisplayLabel)
        octave_layout.addWidget(self.lowOctaveButton)

    def _setup_control_buttons(self):
        # Setup control buttons section
        button_style = """
            QPushButton {
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 5px;
                padding: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-color: #4a90e2;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """
        
        # Chord Finder button
        self.buttonChordFind = QPushButton(self.centralwidget)
        self.buttonChordFind.setGeometry(QRect(180, 310, 140, 30))
        self.buttonChordFind.setText("Chord Finder")
        self.buttonChordFind.setStyleSheet(button_style)
        
        # Chord Progression button
        self.buttonChordProgression = QPushButton(self.centralwidget)
        self.buttonChordProgression.setGeometry(QRect(325, 310, 140, 30))
        self.buttonChordProgression.setText("Chord Progression")
        self.buttonChordProgression.setStyleSheet(button_style)
        
        # Learning Mode button
        self.buttonLearningMode = QPushButton(self.centralwidget)
        self.buttonLearningMode.setGeometry(QRect(180, 345, 285, 30))
        self.buttonLearningMode.setText("Learning Mode")
        self.buttonLearningMode.setStyleSheet(button_style)

    def _setup_status_bar(self):
        # Setup status bar section
        self.statusbar = QtWidgets.QStatusBar(self.mw)
        self.statusbar.setObjectName("statusbar")
        self.mw.setStatusBar(self.statusbar)

    def _connect_signals(self):
        # Connect all signals to their respective slots
        # Volume control
        self.volumeSlider.valueChanged.connect(self.set_volume)
        
        # Octave controls
        self.lowOctaveButton.clicked.connect(self.decrease_octave)
        self.highOctaveButton.clicked.connect(self.increase_octave)
        
        # Control buttons
        self.buttonChordFind.clicked.connect(self.open_chord_finder)
        self.buttonChordProgression.clicked.connect(self.open_chord_progression)
        self.buttonLearningMode.clicked.connect(self.enter_learning_mode)

    def _finalize_setup(self):
        # Finalize the UI setup
        self.retranslateUi(self.mw)
        QtCore.QMetaObject.connectSlotsByName(self.mw)

    # Piano Keyboards Creation Section

    def _create_piano_buttons(self):
        # Create the piano keyboard buttons
        # Keyboard mappings
        keyboard_white = ["Z", "X", "C", "V", "B", "N", "M", "Q", "W", "E", "R", "T", "Y", "U", "I"]
        keyboard_black = ["S", "D", " ", "G", "H", "J", "2", "3", " ", "5", "6", "7"]
        
        # Note labels
        labels_white = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6"]
        labels_black = ["C#4", "D#4", " ", "F#4", "G#4", "A#4", " ", "C#5", "D#5", " ", "F#5", "G#5", "A#5"]
        
        # Create white keys
        self._create_white_keys(keyboard_white, labels_white)
        
        # Create black keys
        self._create_black_keys(keyboard_black, labels_black)

    def _create_white_keys(self, keyboard_white, labels_white):
        # Create white piano keys
        for i, label in enumerate(labels_white):
            button = QPushButton(self.centralwidget)
            button.setGeometry(QtCore.QRect((40*i)+20, 30, 41, 181))
            button.setObjectName(label)
            
            # Connect events
            button.clicked.connect(functools.partial(self.handle_key_click, button))
            button.pressed.connect(lambda key=label: self.notes_sound(key, self.volume, self.octave_shift))
            
            # Add keyboard shortcut
            if i < len(keyboard_white):
                shortcut = QShortcut(self.centralwidget)
                shortcut.setKey(QKeySequence(keyboard_white[i]))
                shortcut.activated.connect(button.click)
            
            self.buttons[label] = button

    def _create_black_keys(self, keyboard_black, labels_black):
        # Create black piano keys
        for i, label in enumerate(labels_black):
            if i != 2 and label != " ":  # Skip positions where there are no black keys
                button = QPushButton(self.centralwidget)
                button.setGeometry(QtCore.QRect((40*i)+40, 30, 31, 111))
                button.setObjectName(label)
                
                # Connect events
                button.clicked.connect(functools.partial(self.handle_key_click, button))
                button.pressed.connect(lambda key=label: self.notes_sound(key, self.volume, self.octave_shift))
                
                # Add keyboard shortcut
                if i < len(keyboard_black) and keyboard_black[i] != " ":
                    shortcut = QShortcut(self.centralwidget)
                    shortcut.setKey(QKeySequence(keyboard_black[i]))
                    shortcut.activated.connect(button.click)
                
                self.buttons[label] = button

    def _apply_piano_styling(self):
        # Apply visual styling to piano keys        
        # Apply styles to all keys
        for button in self.buttons.values():
            name = button.objectName()
            if "#" in name:
                button.setStyleSheet(self._black_key_style())
            else:
                button.setStyleSheet(self._white_key_style())
        
        # Store pressed styles for animation effects
        self._store_pressed_styles()

    def _white_key_style(self):
        # White key style
        return '''
            background-color: qlineargradient(
                spread:pad, x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(255, 255, 255, 255),
                stop:0.5 rgba(240, 240, 240, 255),
                stop:1 rgba(210, 210, 210, 255)
            );
            border: 1px solid rgba(0, 0, 0, 200);
            border-radius: 0px 0px 3px 3px;
        '''
        
    def _black_key_style(self):    
        # Black key style
        return '''
            background-color: qlineargradient(
                spread:pad, x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(40, 40, 40, 255),
                stop:0.5 rgba(20, 20, 20, 255),
                stop:1 rgba(5, 5, 5, 255)
            );
            border: 1px solid rgba(0, 0, 0, 255);
            border-radius: 0px 0px 2px 2px;
        '''

    def _store_pressed_styles(self):
        # Store pressed styles for key animation
        self.white_key_pressed_style = '''
            background-color: qlineargradient(
                spread:pad, x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(210, 230, 255, 255),
                stop:0.5 rgba(150, 200, 255, 255),
                stop:1 rgba(100, 180, 255, 255)
            );
            border: 1px solid rgba(0, 0, 0, 200);
            border-radius: 0px 0px 3px 3px;
        '''
        
        self.black_key_pressed_style = '''
            background-color: qlineargradient(
                spread:pad, x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(80, 100, 120, 255),
                stop:0.5 rgba(40, 60, 100, 255),
                stop:1 rgba(20, 40, 80, 255)
            );
            border: 1px solid rgba(0, 0, 0, 255);
            border-radius: 0px 0px 2px 2px;
        '''

    # Audio & Visual Interactions Section

    def set_volume(self, value):
        # Update volume setting
        self.volume = value
        self.volumeValueLabel.setText(f"{value}")

    def notes_sound(self, note, volume, octave_shift):
        # Play sound for a given note
        if self.octave_shift != 0 and len(note) > 1 and note[-1].isdigit():
            # Extract base note and octave
            base_note = note[:-1]
            original_octave = int(note[-1])
            
            # Apply the octave shift
            new_octave = original_octave + octave_shift
            
            # Create new note name with adjusted octave
            adjusted_note = base_note + str(new_octave)
            
            # Pass 0 as octave shift since we've already applied it to the note name
            self.sound_engine.play_note(adjusted_note, volume, 0)
        else:
            # Normal case - pass the octave shift directly
            self.sound_engine.play_note(note, volume, octave_shift)

    def play_success_sound(self):
        # Play success sound for correct answers
        self.sound_engine.play_success_sound(self.volume)

    def play_error_sound(self):
        # Play error sound for wrong answers
        self.sound_engine.play_error_sound(self.volume)

    def handle_key_click(self, button):
        # Handle piano key click events
        sender = self.mw.sender()
        note_name = sender.objectName()
        
        # Extract note info
        if len(note_name) > 1 and note_name[-1].isdigit():
            base_note = note_name[:-1]
            original_octave = int(note_name[-1])
        else:
            base_note = note_name
            original_octave = 4
        
        # Calculate actual octave with shift
        actual_octave = original_octave + self.octave_shift
        actual_note_name = base_note + str(actual_octave)
        octave_name = self.octave_names.get(actual_octave, f"Octave {actual_octave}")
        
        # Update display
        self.notelabel.setText(f"{actual_note_name} ({octave_name} octave, shifted by {self.octave_shift})")
        
        # Play sound and animate
        QTimer.singleShot(0, lambda: self.notes_sound(note_name, self.volume, self.octave_shift))
        self._animate_key_press(button)

    def _animate_key_press(self, button):
        # Animate key press visual feedback
        # Apply pressed style
        if "#" not in button.objectName():
            button.setStyleSheet(self.white_key_pressed_style)
        else:
            button.setStyleSheet(self.black_key_pressed_style)
        
        # Reset after 100ms
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(functools.partial(self._reset_button, button))
        self.timer.start(100)
        
        # Visual feedback
        button.setChecked(True)
        button.setChecked(False)

    def _reset_button(self, button):
        # Reset button to original style
        name = button.objectName()
        if "#" in name:
            button.setStyleSheet(self._black_key_style())
        else:
            button.setStyleSheet(self._white_key_style())

    def reset_all_piano_highlights(self):
        # Reset all piano key highlights
        for button in self.buttons.values():
            self._reset_button(button)

    def _reset_button_to_default(self, button):
        # Reset single button to default state
        self._reset_button(button)

    # Octave Control Section

    def increase_octave(self):
        # Increase octave shift
        if self.octave_shift < 5:
            self.octave_shift += 1
            self._update_octave_display()

    def decrease_octave(self):
        # Decrease octave shift
        if self.octave_shift > -5:
            self.octave_shift -= 1
            self._update_octave_display()

    def _update_octave_display(self):
        # Update octave display and related UI
        self.octaveDisplayLabel.setText(f"{self.octave_shift}")
        self._update_status_message()
        self._update_chord_displays()

    def _update_status_message(self):
        # Update status bar with octave information
        actual_octave = 4 + self.octave_shift
        octave_name = self.octave_names.get(actual_octave, f"Octave {actual_octave}")
        self.mw.statusBar().showMessage(f"Octave shift: {self.octave_shift} ({octave_name} octave)")

    def _update_chord_displays(self):
        # Update chord displays when octave changes
        # Update chord window if exists
        if hasattr(self, 'chordWindow') and self.chordWindow and hasattr(self.chordWindow, 'chord') and self.chordWindow.chord:
            adjusted_chord = []
            for note in self.chordWindow.chord:
                if len(note) > 1 and note[-1].isdigit():
                    base_note = note[:-1]
                    original_octave = int(note[-1])
                    new_octave = original_octave + self.octave_shift
                    adjusted_chord.append(base_note + str(new_octave))
                else:
                    adjusted_chord.append(note)
            
            chord_text = " ".join(adjusted_chord)
            self.chordWindow.label.setText(f"Chord composed: {chord_text}")
        
        # Update progression window if exists
        if hasattr(self, 'progressionWindow') and self.progressionWindow:
            self.progressionWindow.update_octave_display()

    # Window Managements Section

    def open_chord_finder(self):
        # Open chord finder window
        self.chordWindow = ChordWindow(self)
        self.chordWindow.chordComposed.connect(self.update_note_label)
        self.chordWindow.setWindowTitle("Chord Finder")
        self.chordWindow.resize(300, 200)
        self.chordWindow.move(1300, 200)
        self.chordWindow.show()

    def open_chord_progression(self):
        # Open chord progression window
        # Open chord finder if not already open
        if not hasattr(self, 'chordWindow') or not self.chordWindow.isVisible():
            self.chordWindow = ChordWindow(self)
            self.chordWindow.chordComposed.connect(self.update_note_label)
            self.chordWindow.setWindowTitle("Chord Finder")
            self.chordWindow.resize(300, 200)
            self.chordWindow.move(1300, 200)
            self.chordWindow.show()
        
        # Open progression window if not already open
        if not hasattr(self, 'progressionWindow') or not self.progressionWindow.isVisible():
            self.progressionWindow = ChordProgressionWindow(self)
            self.progressionWindow.move(1300, 450)
            self.progressionWindow.show()

        # Connect signals between windows
        if hasattr(self, 'chordWindow') and hasattr(self, 'progressionWindow'):
            self.chordWindow.composer.chordComposed.connect(
                lambda chordName, chord: self.progressionWindow.set_root_chord(
                    chord[0], self.chordWindow.chordTypeCombo.currentText()
                )
            )

    def update_note_label(self, chord_name):
        # Update the note label when a chord is selected
        self.notelabel.setText(chord_name)

    # Learning Mode Section

    def enter_learning_mode(self):
        # Switch to learning mode
        # Hide normal controls
        self.buttonChordFind.hide()
        self.buttonChordProgression.hide()
        self.octaveControlFrame.hide()
        self.buttonLearningMode.hide()
        self.statusbar.hide()

        # Disable keyboard shortcuts
        self._disable_keyboard_shortcuts()
        
        # Create and show learning interface
        if not self.learning_ui:
            from learning_system.learning_mode_ui import LearningModeUI
            self.learning_ui = LearningModeUI(self)
        
        self.learning_ui.show_learning_interface()
        self.learning_mode_active = True
        
        # Update UI
        self.mw.setWindowTitle("Piano Learning Mode")
        self.notelabel.setText("Learning Mode Active")

    def exit_learning_mode(self):
        # Exit learning mode
        # Hide learning interface
        if self.learning_ui:
            self.learning_ui.hide_learning_interface()
        
        # Show normal controls
        self.buttonChordFind.show()
        self.buttonChordProgression.show()
        self.octaveControlFrame.show()
        self.buttonLearningMode.show()
        self.statusbar.show()
        
        # Re-enable keyboard shortcuts
        self._enable_keyboard_shortcuts()

        # Reset and restore
        self.reset_all_piano_highlights()
        self.learning_mode_active = False
        self.mw.setWindowTitle("Piano Chord Learning App")
        self.notelabel.setText("No chord selected")

    def _disable_keyboard_shortcuts(self):
        # Disable keyboard shortcuts
        if not hasattr(self, 'stored_shortcuts'):
            self.stored_shortcuts = []
        
        for child in self.centralwidget.findChildren(QShortcut):
            self.stored_shortcuts.append(child)
            child.setEnabled(False)

    def _enable_keyboard_shortcuts(self):
        # Re-enable keyboard shortcuts
        if hasattr(self, 'stored_shortcuts'):
            for shortcut in self.stored_shortcuts:
                shortcut.setEnabled(True)

    # Utility Section

    def _get_button_from_note(self, note):
        # Find button object corresponding to a note name
        for button in self.buttons.values():
            if button.objectName() == note:
                return button
        return None

    def retranslateUi(self, MainWindow):
        # Set up text translations for UI elements
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Piano Chord Learning App"))

    def cleanup(self):
        # Clean up resources when closing
        # Clean up sound engine
        if hasattr(self, 'sound_engine'):
            self.sound_engine.cleanup()
        
        # Close child windows
        if hasattr(self, 'chordWindow') and self.chordWindow:
            self.chordWindow.close()
        
        if hasattr(self, 'progressionWindow') and self.progressionWindow:
            self.progressionWindow.close()