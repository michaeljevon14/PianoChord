from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import *
from note_converter import NoteConverter
from learning_system.modes.missing_note import MissingNoteMode
from learning_system.difficulty_manager import DifficultyManager
from learning_system.modes.chord_construction import ChordConstructionMode
from learning_system.modes.chord_identification import ChordIdentificationMode

# Main UI controller for learning mode
class LearningModeUI:
    
    def __init__(self, main_window):
        self.main_window = main_window
        
        # Learning state
        self.current_mode = "identification"
        self.current_difficulty = "easy"
        self.session_active = False
        self.current_question_num = 0
        self.total_questions = 0
        self.session_score = 0
        self.correct_answers = 0
        
        # Mode handlers - pass self to give them access to notation methods
        self.chord_identification = ChordIdentificationMode(main_window, self)
        self.missing_note = MissingNoteMode(main_window, self)
        self.chord_construction = ChordConstructionMode(main_window, self)
        
        # UI elements (will be created)
        self.learning_widgets = {}
        
        self.create_learning_widgets()
        self.on_difficulty_changed()
    
    def get_piano_button_for_note(self, note):
        # Get the piano button object for a given note (handles notation conversion)
        # Convert to sharp notation for piano button lookup
        piano_note = NoteConverter.convert_for_piano_button(note)
        return self.main_window.buttons.get(piano_note)

    def play_note_with_conversion(self, note, volume=None, octave_shift=0):
        # Play a note with automatic notation conversion for piano compatibility
        if volume is None:
            volume = self.main_window.volume
        
        # Convert to sharp notation for sound engine
        piano_note = NoteConverter.convert_for_piano_button(note)
        self.main_window.notes_sound(piano_note, volume, octave_shift)

    def highlight_note_on_piano(self, note, style):
        # Highlight a note on the piano with automatic notation conversion
        button = self.get_piano_button_for_note(note)
        if button:
            button.setStyleSheet(style)

    def is_same_note(self, note1, note2, chord_type=None):
        # Compare two notes considering enharmonic equivalents
        return NoteConverter.is_enharmonic_equivalent(note1, note2)

    def get_note_display_name(self, note, chord_type=None):
        # Get the display name for a note (without octave) with proper notation
        return NoteConverter.get_display_name(note, chord_type)
    
    def create_learning_widgets(self):
        # Create all learning mode UI elements
        centralwidget = self.main_window.centralwidget
        
        # Header area - Mode selection and progress
        self.learning_widgets['header'] = QWidget(centralwidget)
        self.learning_widgets['header'].setGeometry(20, 5, 600, 25)
        header_layout = QHBoxLayout(self.learning_widgets['header'])
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Mode selection
        header_layout.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Chord Identification", "Missing Note", "Chord Construction"])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        self.mode_combo.setFixedWidth(140)
        header_layout.addWidget(self.mode_combo)
        
        # Difficulty selection
        header_layout.addWidget(QLabel("Level:"))
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Easy", "Medium"])
        self.difficulty_combo.currentTextChanged.connect(self.on_difficulty_changed)
        self.difficulty_combo.setFixedWidth(80)
        header_layout.addWidget(self.difficulty_combo)
        
        # Progress display
        self.progress_label = QLabel("Ready to start")
        self.progress_label.setFixedWidth(100)
        header_layout.addWidget(self.progress_label)

        # Spacer
        header_layout.addStretch()
        
        # Exit button
        self.exit_button = QPushButton("Exit Learning Mode")
        self.exit_button.clicked.connect(self.try_exit_learning_mode)
        self.exit_button.setFixedWidth(130)
        self.exit_button.setStyleSheet("background-color: #ffcccc;")
        header_layout.addWidget(self.exit_button)
        
        # Question display area (replaces the note label area)
        self.learning_widgets['question'] = QLabel(centralwidget)
        self.learning_widgets['question'].setGeometry(80, 230, 480, 40)
        self.learning_widgets['question'].setAlignment(Qt.AlignCenter)
        self.learning_widgets['question'].setStyleSheet('''
            border: 2px solid #4a90e2;
            border-radius: 6px;
            padding: 6px;
            font-size: 14px;
            font-weight: bold;
            background-color: #e8f4fd;
            color: #2c5aa0;
        ''')
        self.learning_widgets['question'].setText("Click 'Start Session' to begin!")
        
        # Control buttons area (below piano)
        self.learning_widgets['controls'] = QWidget(centralwidget)
        self.learning_widgets['controls'].setGeometry(120, 275, 400, 35)
        controls_layout = QHBoxLayout(self.learning_widgets['controls'])
        controls_layout.setContentsMargins(0, 0, 0, 0)
        
        self.start_button = QPushButton("Start Session")
        self.start_button.clicked.connect(self.start_session)
        self.start_button.setFixedSize(90, 30)
        self.start_button.setStyleSheet("background-color: #90ee90; font-weight: bold;")
        controls_layout.addWidget(self.start_button)
        
        self.play_again_button = QPushButton("Play Again")
        self.play_again_button.clicked.connect(self.replay_current_question)
        self.play_again_button.setEnabled(False)
        self.play_again_button.setFixedSize(90, 30)
        controls_layout.addWidget(self.play_again_button)
        
        self.hint_button = QPushButton("Show Hint")
        self.hint_button.clicked.connect(self.show_hint)
        self.hint_button.setEnabled(False)
        self.hint_button.setFixedSize(100, 30)
        controls_layout.addWidget(self.hint_button)
        
        self.next_button = QPushButton("Next Question")
        self.next_button.clicked.connect(self.next_question)
        self.next_button.setEnabled(False)
        self.next_button.setFixedSize(90, 30)
        self.next_button.setStyleSheet("background-color: #add8e6;")
        controls_layout.addWidget(self.next_button)
        
        # Answer area (multiple choice buttons)
        self.learning_widgets['answers'] = QWidget(centralwidget)
        self.learning_widgets['answers'].setGeometry(80, 320, 480, 50)
        self.answer_layout = QVBoxLayout(self.learning_widgets['answers'])
        self.answer_layout.setContentsMargins(0, 0, 0, 0)
        self.answer_buttons = []
        
        # Status bar (bottom)
        self.learning_widgets['status'] = QLabel(centralwidget)
        self.learning_widgets['status'].setGeometry(20, 380, 600, 20)
        self.learning_widgets['status'].setAlignment(Qt.AlignCenter)
        self.learning_widgets['status'].setStyleSheet("color: #666; font-size: 12px;")
        self.learning_widgets['status'].setText("Select difficulty and click 'Start Session'")
        
        # Initially hide all widgets
        self.hide_learning_interface()
    
    def show_learning_interface(self):
        # Show all learning mode UI elements
        for widget in self.learning_widgets.values():
            widget.show()
    
    def hide_learning_interface(self):
        # Hide all learning mode UI elements
        for widget in self.learning_widgets.values():
            widget.hide()
    
    def on_mode_changed(self):
        # Handle mode selection change
        selected_mode = self.mode_combo.currentText()
        if selected_mode == "Chord Identification":
            self.current_mode = "identification"
            self.hint_button.setText("Show Answer")
        elif selected_mode == "Missing Note":
            self.current_mode = "missing_note"
            self.hint_button.setText("Intervals")
        elif selected_mode == "Chord Construction":
            self.current_mode = "chord_construction"
            self.hint_button.setText("Play Target")
        
        # Reset session if mode changes during active session
        if self.session_active:
            self.reset_all_session_data()

    def update_question_display_for_piano(self, question_text):
        # Update question display for piano interaction modes
        self.learning_widgets['question'].setText(question_text)
        # Clear any existing answer buttons since we'll use piano
        self.clear_answer_buttons()

    def on_difficulty_changed(self):
        # Handle difficulty level change
        selected_text = self.difficulty_combo.currentText() if hasattr(self, 'difficulty_combo') else "Easy"
        self.current_difficulty = selected_text.lower()
        config = DifficultyManager.get_config(self.current_difficulty)
        self.total_questions = config["questions_per_session"]
        
        if not self.session_active:
            status_text = (
                f"Level: {self.current_difficulty.title()} "
                f"({self.total_questions} questions) - Click 'Start Session'"
            )
            if hasattr(self, 'learning_widgets') and 'status' in self.learning_widgets:
                self.learning_widgets['status'].setText(status_text)
    
    def start_session(self):
        # Start a new learning session
        self.session_active = True
        self.current_question_num = 0
        self.session_score = 0
        self.correct_answers = 0
        
        # Update UI state
        self.start_button.setEnabled(False)
        self.difficulty_combo.setEnabled(False)
        self.play_again_button.setEnabled(True)
        self.hint_button.setEnabled(True)
        
        # Start first question
        self.next_question()
    
    def next_question(self):
        # Generate and present the next question
        self.current_question_num += 1
        
        # Check if session should end
        if self.current_question_num > self.total_questions:
            self.end_session()
            return
        
        self.update_progress_display()

        # Reset piano highlights before starting new question
        self.main_window.reset_all_piano_highlights()
        
        # Reset UI for next question
        self.clear_answer_buttons()
        self.next_button.setText("Next Question")
        self.next_button.setEnabled(False)
        
        # Generate question based on current mode
        if self.current_mode == "identification":
            success = self.chord_identification.start_question(self.current_difficulty)
        elif self.current_mode == "missing_note":
            success = self.missing_note.start_question(self.current_difficulty)
        elif self.current_mode == "chord_construction":
            success = self.chord_construction.start_question(self.current_difficulty)
        else:
            success = False
        
        if not success:
            self.learning_widgets['question'].setText("Error generating question")
    
    def update_question_display(self, question_text, answer_choices):
        # Update the question display and answer choices
        self.learning_widgets['question'].setText(question_text)
        self.create_answer_buttons(answer_choices)
    
    def create_answer_buttons(self, choices):
        # Create multiple choice answer buttons
        self.clear_answer_buttons()
    
        # Create horizontal layout for answer buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        for choice in choices:
            button = QPushButton(choice)
            button.clicked.connect(lambda checked, c=choice: self.submit_answer(c))
            button.setFixedSize(110, 35)
            button.setStyleSheet('''
                QPushButton {
                    background-color: #f0f0f0;
                    border: 2px solid #ccc;
                    border-radius: 6px;
                    padding: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                    border-color: #4a90e2;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                }
            ''')
            self.answer_buttons.append(button)
            button_layout.addWidget(button)
        
        self.answer_layout.addLayout(button_layout)
    
    def clear_answer_buttons(self):
        # Clear existing answer buttons
        for button in self.answer_buttons:
            button.deleteLater()
        self.answer_buttons.clear()
        
        # Clear layout
        while self.answer_layout.count():
            child = self.answer_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def submit_answer(self, selected_answer):
        # Process submitted answer
        # Disable all answer buttons
        for button in self.answer_buttons:
            button.setEnabled(False)
        
        # Process answer based on current mode
        if self.current_mode == "identification":
            result = self.chord_identification.submit_answer(selected_answer)
            self.process_answer_result(result)
    
    def process_answer_result(self, result):
        # Process the result of an answered question
        if result["correct"]:
            self.correct_answers += 1
            feedback = f"Correct! (+{result['score']} points)"
            
            # Play success sound
            self.main_window.play_success_sound()
        else:
            feedback = f"Wrong. Correct answer: {result['correct_answer']}"

            # Play error sound
            self.main_window.play_error_sound()            
        
        self.session_score += result["score"]
        
        # Update status
        self.learning_widgets['status'].setText(
            f"{feedback} | Score: {self.session_score} | "
            f"Correct: {self.correct_answers}/{self.current_question_num}"
        )
        
        # Enable next button
        self.next_button.setEnabled(True)
    
    def replay_current_question(self):
        # Replay the current question
        if self.current_mode == "identification":
            self.chord_identification.replay_chord()
        elif self.current_mode == "missing_note":
            self.missing_note.replay_chord()
        elif self.current_mode == "chord_construction":
            self.chord_construction.play_user_chord()
    
    def show_hint(self):
        # Show hint for current question
        if self.current_mode == "identification":
            answer = self.chord_identification.show_answer()
            self.learning_widgets['status'].setText(f"Hint: The answer is {answer}")
        elif self.current_mode == "missing_note":
            hint = self.missing_note.show_hint()
            self.learning_widgets['status'].setText(f"Hint: {hint}")
        elif self.current_mode == "chord_construction":
            hint = self.chord_construction.show_hint()
            self.learning_widgets['status'].setText(f"Hint: {hint}")
    
    def update_progress_display(self):
        # Update the progress display
        self.progress_label.setText(f"Question {self.current_question_num}/{self.total_questions}")
    
    def end_session(self):
        # End the current learning session
        self.session_active = False
        
        # Safety check to prevent division by zero
        if self.total_questions == 0:
            QMessageBox.warning(self.main_window.mw, "Error", "No questions were configured for this session.")
            self.reset_session_ui()
            return

        # Calculate final results
        percentage = (self.correct_answers / self.total_questions) * 100
        
        # Show final results
        result_text = (
            f"Session Complete!\n"
            f"Score: {self.session_score} points\n"
            f"Correct: {self.correct_answers}/{self.total_questions} ({percentage:.1f}%)"
        )
        
        QMessageBox.information(self.main_window.mw, "Session Complete", result_text)
        
        # Reset UI
        self.reset_session_ui()
    
    def reset_session_ui(self):
        # Reset UI to pre-session state
        self.start_button.setEnabled(True)
        self.difficulty_combo.setEnabled(True)
        self.play_again_button.setEnabled(False)
        self.hint_button.setEnabled(False)
        self.next_button.setEnabled(False)
        
        # Clear displays
        self.clear_answer_buttons()
        self.learning_widgets['question'].setText("Click 'Start Session' to begin!")
        self.progress_label.setText("Ready to start")

        # Reset status based on current difficulty
        config = DifficultyManager.get_config(self.current_difficulty)
        self.learning_widgets['status'].setText(
            f"Level: {self.current_difficulty.title()} "
            f"({config['questions_per_session']} questions) - Click 'Start Session'"
        )
        
        # Reset piano highlights
        if hasattr(self, 'chord_identification'):
            self.chord_identification.cleanup()

    def try_exit_learning_mode(self):
        # Check if session is active and warn user before exiting
        if self.session_active:
            # Show warning dialog
            reply = QMessageBox.question(
                self.main_window.mw,
                "Session In Progress", 
                "You have a learning session in progress.\n\n"
                "Are you sure you want to exit?\n"
                "Your current progress will be lost.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No  # Default to No
            )
            
            if reply == QMessageBox.Yes:
                self.force_exit_learning_mode()
            # If No, do nothing - stay in learning mode
        else:
            # No active session, safe to exit
            self.main_window.exit_learning_mode()

    def force_exit_learning_mode(self):
        # Force exit learning mode and reset everything
        # End any active session
        if self.session_active:
            self.session_active = False
            
        # Reset all session data
        self.reset_all_session_data()
        
        # Exit learning mode
        self.main_window.exit_learning_mode()

    def reset_all_session_data(self):
        # Reset all session data to initial state
        # Reset session variables
        self.session_active = False
        self.current_question_num = 0
        self.session_score = 0
        self.correct_answers = 0
        
        # Reset UI to initial state
        self.reset_session_ui()
        
        # Clean up current modes
        if hasattr(self, 'chord_identification'):
            self.chord_identification.cleanup()
        if hasattr(self, 'missing_note'):
            self.missing_note.cleanup()
        if hasattr(self, 'chord_construction'):
            self.chord_construction.cleanup()

    def show_learning_interface(self):
        # Show all learning mode UI elements and reset session
        # Reset session data when entering learning mode
        self.reset_all_session_data()
        
        # Show UI elements
        for widget in self.learning_widgets.values():
            widget.show()