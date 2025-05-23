import random
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox
from chord_composer import ChordComposer
from learning_system.difficulty_manager import DifficultyManager

class ChordConstructionMode:
    # Mode 3: User builds a chord by clicking piano keys
    
    def __init__(self, main_window, learning_ui):
        self.main_window = main_window
        self.learning_ui = learning_ui
        self.composer = ChordComposer()
        
        # Current question state
        self.current_question = None
        self.target_chord_notes = []
        self.user_selected_notes = []
        self.correct_answer = None
        
    def start_question(self, difficulty):
        # Start a new chord construction question
        # Generate random chord based on difficulty
        root_note, chord_type = DifficultyManager.generate_random_chord(difficulty)
        
        # Generate the target chord notes
        chord_name, chord_notes = self.composer.composeChord(root_note + "4", chord_type)
        
        # Store question data
        self.current_question = {
            "root_note": root_note,
            "chord_type": chord_type,
            "difficulty": difficulty,
            "chord_name": chord_name
        }
        self.target_chord_notes = set(chord_notes)  # Use set for easy comparison
        self.correct_answer = f"{root_note} {chord_type}"
        self.user_selected_notes = []
        
        # Update UI
        question_text = f"Build: {root_note} {chord_type}"
        self.learning_ui.update_question_display_for_piano(question_text)
        
        # Enable piano interaction for this mode
        self.setup_piano_interaction()
        
        # Reset all highlights to start clean
        self.main_window.reset_all_piano_highlights()

        return True

    def setup_piano_interaction(self):
        # Enable piano clicks for chord construction mode
        for note, button in self.main_window.buttons.items():
            # Disconnect any existing connections to avoid duplicates
            try:
                button.clicked.disconnect()
            except:
                pass
            
            # Connect to chord construction handler
            button.clicked.connect(lambda checked, n=note: self.handle_piano_click(n))

    def cleanup_piano_interaction(self):
        # Disable piano interaction after answer submission
        for button in self.main_window.buttons.values():
            try:
                button.clicked.disconnect()
            except:
                pass

    def handle_piano_click(self, clicked_note):
        # Handle when user clicks a piano key
        # Toggle behavior - if already selected, remove it; if not, add it
        if clicked_note in self.user_selected_notes:
            self.remove_note_selection(clicked_note)
        else:
            self.add_note_selection(clicked_note)
        
        # Update submit button state
        if self.user_selected_notes:
            self.enable_submit_button()
        else:
            self.disable_submit_button()
    
    def add_note_selection(self, note):
        # Add a note to user's chord construction
        if note not in self.user_selected_notes:
            self.user_selected_notes.append(note)
            
            # Highlight the selected note in purple
            # Use learning_ui method to get correct piano button (handles conversion)
            button = self.learning_ui.get_piano_button_for_note(note)
            if button:
                button.setStyleSheet("background-color: rgb(150, 100, 255); border: 2px solid rgb(120, 80, 200);")
    
    def remove_note_selection(self, note):
        # Remove a note from user's chord construction
        if note in self.user_selected_notes:
            self.user_selected_notes.remove(note)
            
            # Reset the button to original style
            # Use learning_ui method to get correct piano button (handles conversion)
            button = self.learning_ui.get_piano_button_for_note(note)
            if button:
                self.main_window._reset_button(button)
    
    def clear_all_selections(self):
        # Clear all user selections
        for note in self.user_selected_notes.copy():
            self.remove_note_selection(note)
    
    def play_user_chord(self):
        # Play the chord user has constructed
        if self.user_selected_notes:
            for note in self.user_selected_notes:
                # Use learning_ui method to play note with conversion
                self.learning_ui.play_note_with_conversion(note, self.main_window.volume, 0)
        return len(self.user_selected_notes) > 0
    
    def play_target_chord(self):
        # Play the target chord (for feedback)
        for note in self.target_chord_notes:
            # Use learning_ui method to play note with conversion
            self.learning_ui.play_note_with_conversion(note, self.main_window.volume, 0)

    def enable_submit_button(self):
        # Enable submit button after user makes selections
        self.learning_ui.next_button.setText("Submit Chord")
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
        # Process user's submitted chord construction
        if not self.user_selected_notes:
            return None
        
        # Convert user selection to set for comparison, accounting for enharmonic equivalents
        user_chord_set = set(self.user_selected_notes)
        target_chord_set = set(self.target_chord_notes)
        
        # Check if user's chord matches the target chord, considering enharmonic equivalents
        chord_type = self.current_question.get("chord_type")
        is_correct = self._compare_chord_sets(user_chord_set, target_chord_set, chord_type)
        
        # Show visual feedback
        if is_correct:
            self.show_correct_feedback()
        else:
            self.show_incorrect_feedback()
        
        # Calculate score
        score = self.calculate_score(is_correct)
        
        # Disable piano interaction
        self.cleanup_piano_interaction()
        
        # Create user answer string for display
        user_notes = [self.learning_ui.get_note_display_name(note, chord_type) for note in self.user_selected_notes]
        user_answer_text = " ".join(sorted(user_notes))
        
        # Return result data
        return {
            "correct": is_correct,
            "user_answer": user_answer_text,
            "correct_answer": self.correct_answer,
            "score": score
        }
    
    def _compare_chord_sets(self, user_set, target_set, chord_type):
        # Compare two chord sets considering enharmonic equivalents
        if len(user_set) != len(target_set):
            return False
        
        # For each note in target set, check if there's an enharmonic equivalent in user set
        for target_note in target_set:
            found_match = False
            for user_note in user_set:
                if self.learning_ui.is_same_note(target_note, user_note, chord_type):
                    found_match = True
                    break
            if not found_match:
                return False
        
        return True

    def show_correct_feedback(self):
        # Show green highlighting for correct answer
        # Show all target chord notes in green
        for note in self.target_chord_notes:
            # Use learning_ui method to get correct piano button (handles conversion)
            button = self.learning_ui.get_piano_button_for_note(note)
            if button:
                button.setStyleSheet("background-color: rgb(80, 200, 80); border: 2px solid rgb(60, 150, 60);")
        
        # Play the correct chord
        QTimer.singleShot(1800, self.play_target_chord)
    
    def show_incorrect_feedback(self):
        # Show feedback for incorrect answer
        # Show user's wrong selections in red
        for note in self.user_selected_notes:
            # Use learning_ui method to get correct piano button (handles conversion)
            button = self.learning_ui.get_piano_button_for_note(note)
            if button:
                button.setStyleSheet("background-color: rgb(255, 100, 100); border: 2px solid rgb(200, 80, 80);")
        
        # After 1.5 seconds, show correct answer in green
        QTimer.singleShot(800, self.show_correct_feedback)
    
    def calculate_score(self, is_correct):
        # Calculate score based on correctness
        if not is_correct:
            return 0
        
        config = DifficultyManager.get_config(self.current_question["difficulty"])
        base_score = config["points_per_correct"]
        
        return base_score
    
    def show_hint(self):
        # Show hint by playing the target chord
        self.play_target_chord()
        
        # Show interval information
        chord_type = self.current_question['chord_type']
        root_note = self.current_question['root_note']
        
        interval_info = {
            "major": "Root + Major 3rd (4 semitones) + Perfect 5th (7 semitones)",
            "minor": "Root + Minor 3rd (3 semitones) + Perfect 5th (7 semitones)", 
            "diminished": "Root + Minor 3rd (3 semitones) + Diminished 5th (6 semitones)"
        }
        
        intervals = interval_info.get(chord_type, "Unknown chord type")
        
        msg_box = QMessageBox(self.main_window.mw)
        msg_box.setWindowTitle(f"Hint: {root_note.title()} {chord_type.title()} Chord")
        msg_box.setText(f"Listen to the target chord!\n\nIntervals:\n{intervals}")
        msg_box.setIcon(QMessageBox.NoIcon)  # Remove the icon to avoid sound
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
        
        return f"Played target chord and showed intervals for {root_note} {chord_type}"
    
    def show_answer(self):
        # Show the correct answer
        self.show_correct_feedback()
        chord_type = self.current_question.get("chord_type")
        target_notes = [self.learning_ui.get_note_display_name(note, chord_type) for note in self.target_chord_notes]
        return f"Correct notes: {' '.join(sorted(target_notes))}"
    
    def reset_piano_highlights(self):
        # Reset all piano highlights to original state
        self.main_window.reset_all_piano_highlights()
    
    def cleanup(self):
        # Clean up mode state
        self.reset_piano_highlights()
        self.current_question = None
        self.target_chord_notes = []
        self.user_selected_notes = []
        self.correct_answer = None