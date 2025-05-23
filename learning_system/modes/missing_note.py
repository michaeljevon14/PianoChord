import random
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox
from chord_composer import ChordComposer
from learning_system.difficulty_manager import DifficultyManager

class MissingNoteMode:
    # Mode 2: User finds the missing note to complete a chord
    
    def __init__(self, main_window, learning_ui):
        self.main_window = main_window
        self.learning_ui = learning_ui
        self.composer = ChordComposer()
        
        # Current question state
        self.current_question = None
        self.complete_chord_notes = []
        self.incomplete_chord_notes = []
        self.missing_note = None
        self.correct_answer = None
        self.user_answer = None
        self.user_selected_notes = []
        
    def start_question(self, difficulty):
        # Start a new missing note question
        # Generate random chord based on difficulty
        root_note, chord_type = DifficultyManager.generate_random_chord(difficulty)
        
        # Generate the complete chord notes
        chord_name, chord_notes = self.composer.composeChord(root_note + "4", chord_type)
        
        # Randomly remove one note from the chord
        missing_note_index = random.randint(0, len(chord_notes) - 1)
        missing_note = chord_notes[missing_note_index]
        incomplete_notes = chord_notes.copy()
        incomplete_notes.pop(missing_note_index)
        
        # Store question data
        self.current_question = {
            "root_note": root_note,
            "chord_type": chord_type,
            "difficulty": difficulty,
            "chord_name": chord_name
        }
        self.complete_chord_notes = chord_notes
        self.incomplete_chord_notes = incomplete_notes
        self.missing_note = missing_note
        self.correct_answer = missing_note
        self.user_answer = None
        self.user_selected_notes = []
        
        # Update UI
        question_text = f"Complete the {root_note} {chord_type} chord by clicking the missing note"
        self.learning_ui.update_question_display_for_piano(question_text)
        
        # Enable piano interaction for this mode
        self.setup_piano_interaction()
        
        # Highlight the incomplete chord and play it
        self.highlight_incomplete_chord()
        self.play_incomplete_chord()
        
        return True

    def setup_piano_interaction(self):
        # Enable piano clicks for missing note mode
        for note, button in self.main_window.buttons.items():
            # Disconnect any existing connections to avoid duplicates
            try:
                button.clicked.disconnect()
            except:
                pass
            
            # Connect to missing note handler
            button.clicked.connect(lambda checked, n=note: self.handle_piano_click(n))

    def cleanup_piano_interaction(self):
        # Disable piano interaction after answer submission
        for button in self.main_window.buttons.values():
            try:
                button.clicked.disconnect()
            except:
                pass

    def highlight_incomplete_chord(self):
        # Highlight the incomplete chord on the piano
        # Reset all highlights first
        self.main_window.reset_all_piano_highlights()
        
        # Highlight present notes in blue
        for note in self.incomplete_chord_notes:
            button = self.main_window.buttons.get(note)
            if button:
                button.setStyleSheet("background-color: rgb(70, 130, 255); border: 2px solid rgb(50, 100, 200);")
        
        # Highlight missing note position with a subtle indicator (optional - shows where it should go)
        # We'll skip this for now to make it more challenging
    
    def play_incomplete_chord(self):
        # Play the incomplete chord sound
        for note in self.incomplete_chord_notes:
            # Use learning_ui method to play note with conversion
            self.learning_ui.play_note_with_conversion(note, self.main_window.volume, 0)
    
    def play_complete_chord(self):
        # Play the complete chord sound (for hint/feedback)
        for note in self.complete_chord_notes:
            # Use learning_ui method to play note with conversion
            self.learning_ui.play_note_with_conversion(note, self.main_window.volume, 0)

    def replay_chord(self):
        # Replay the current incomplete chord
        if self.incomplete_chord_notes:
            self.play_incomplete_chord()
    
    def handle_piano_click(self, clicked_note):
        # Handle when user clicks a piano key
        # Don't allow selecting notes that are already part of the incomplete chord
        if clicked_note in self.incomplete_chord_notes:
            return
        
        # If this note is already selected by user, remove it (toggle behavior)
        if clicked_note in self.user_selected_notes:
            self.remove_selection(clicked_note)
        else:
            # Clear previous selection first (only allow one selection at a time)
            self.clear_user_selections()
            self.add_selection(clicked_note)
    
    def add_selection(self, clicked_note):
        # Add a note selection
        # Store the user's selection
        self.user_answer = clicked_note
        
        # Highlight the user's selection in purple
        # Use learning_ui method to get correct piano button (handles conversion)
        button = self.learning_ui.get_piano_button_for_note(clicked_note)
        if button:
            button.setStyleSheet("background-color: rgb(150, 100, 255); border: 2px solid rgb(120, 80, 200);")
        
        # Add to user selected notes for tracking
        if clicked_note not in self.user_selected_notes:
            self.user_selected_notes.append(clicked_note)
        
        # Enable submit button
        self.enable_submit_button()

    def remove_selection(self, clicked_note):
        # Remove a note selection
        # Remove from user selections
        if clicked_note in self.user_selected_notes:
            self.user_selected_notes.remove(clicked_note)
            
            # If this was the current answer, clear it
            if self.user_answer == clicked_note:
                self.user_answer = None
                
            # Reset the button to original style
            # Use learning_ui method to get correct piano button (handles conversion)
            button = self.learning_ui.get_piano_button_for_note(clicked_note)
            if button:
                self.main_window._reset_button(button)
            
            # Disable submit button if no selections
            if not self.user_selected_notes:
                self.disable_submit_button()

    def clear_user_selections(self):
        # Clear all user selections
        for note in self.user_selected_notes.copy():
            self.remove_selection(note)

    def enable_submit_button(self):
        # Enable submit button after user makes a selection
        self.learning_ui.next_button.setText("Submit Answer")
        self.learning_ui.next_button.setEnabled(True)
        # Disconnect from next_question and connect to submit
        try:
            self.learning_ui.next_button.clicked.disconnect()
        except:
            pass
        self.learning_ui.next_button.clicked.connect(self.submit_from_ui)

    def disable_submit_button(self):
        # Disable submit button when no selection is made
        self.learning_ui.next_button.setText("Next Question")
        self.learning_ui.next_button.setEnabled(False)
        try:
            self.learning_ui.next_button.clicked.disconnect()
        except:
            pass
        self.learning_ui.next_button.clicked.connect(self.learning_ui.next_question)

    def submit_from_ui(self):
        # Submit answer and process result
        result = self.submit_answer()
        if result:
            self.learning_ui.process_answer_result(result)
            # Change button back to "Next Question"
            self.learning_ui.next_button.setText("Next Question")
            self.learning_ui.next_button.clicked.disconnect()
            self.learning_ui.next_button.clicked.connect(self.learning_ui.next_question)

    def submit_answer(self):
        # Process user's submitted answer
        if not self.user_answer:
            return None
        
        # Check if answer is correct using enharmonic comparison
        chord_type = self.current_question.get("chord_type")
        is_correct = self.learning_ui.is_same_note(self.user_answer, self.correct_answer, chord_type)
        
        # Show visual feedback
        if is_correct:
            self.show_correct_feedback()
        else:
            self.show_incorrect_feedback()
        
        # Calculate score
        score = self.calculate_score(is_correct)
        
        # Disable piano interaction
        self.cleanup_piano_interaction()
        
        # Return result data
        return {
            "correct": is_correct,
            "user_answer": self.user_answer,
            "correct_answer": self.correct_answer,
            "score": score
        }
    
    def show_correct_feedback(self):
        # Show green highlighting for correct answer
        # Show the complete chord in green
        for note in self.complete_chord_notes:
            # Use learning_ui method to get correct piano button (handles conversion)
            button = self.learning_ui.get_piano_button_for_note(note)
            if button:
                button.setStyleSheet("background-color: rgb(80, 200, 80); border: 2px solid rgb(60, 150, 60);")
        
        # Play the complete chord
        QTimer.singleShot(1800, self.play_complete_chord)
    
    def show_incorrect_feedback(self):
        # Show red highlighting for incorrect answer, then show correct answer
        # Show user's wrong selection in red
        if self.user_answer:
            # Use learning_ui method to get correct piano button (handles conversion)
            button = self.learning_ui.get_piano_button_for_note(self.user_answer)
            if button:
                button.setStyleSheet("background-color: rgb(255, 100, 100); border: 2px solid rgb(200, 80, 80);")
        
        # After 1 second, show correct complete chord in green
        QTimer.singleShot(800, self.show_correct_feedback)
    
    def calculate_score(self, is_correct):
        # Calculate score based on correctness
        if not is_correct:
            return 0
        
        config = DifficultyManager.get_config(self.current_question["difficulty"])
        base_score = config["points_per_correct"]
        
        return base_score
    
    def show_hint(self):
        # Show hint by playing the complete chord
        chord_type = self.current_question['chord_type']
        root_note = self.current_question['root_note']
        
        # Define intervals for each chord type
        interval_info = {
            "major": "Root + Major 3rd (4 semitones) + Perfect 5th (7 semitones)",
            "minor": "Root + Minor 3rd (3 semitones) + Perfect 5th (7 semitones)", 
            "diminished": "Root + Minor 3rd (3 semitones) + Diminished 5th (6 semitones)"
        }
        
        # Get the interval description
        intervals = interval_info.get(chord_type, "Unknown chord type")
        
        # Show simple message box
        msg_box = QMessageBox(self.main_window.mw)
        msg_box.setWindowTitle(f"{root_note.title()} {chord_type.title()} Chord")
        msg_box.setText(f"Intervals:\n{intervals}")
        msg_box.setIcon(QMessageBox.NoIcon)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
        
        return f"Showed intervals for {root_note} {chord_type}"
    
    def show_answer(self):
        # Show the correct answer
        self.show_correct_feedback()
        # Get display name with proper notation for chord type
        chord_type = self.current_question.get("chord_type")
        note_display = self.learning_ui.get_note_display_name(self.missing_note, chord_type)
        return f"The missing note is: {note_display}"
    
    def reset_piano_highlights(self):
        # Reset all piano highlights to original state
        self.main_window.reset_all_piano_highlights()
    
    def cleanup(self):
        # Clean up mode state
        self.reset_piano_highlights()
        self.current_question = None
        self.complete_chord_notes = []
        self.incomplete_chord_notes = []
        self.missing_note = None
        self.correct_answer = None
        self.user_answer = None
        self.user_selected_notes = []