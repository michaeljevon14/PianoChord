from PyQt5.QtCore import QTimer
from chord_composer import ChordComposer
from learning_system.difficulty_manager import DifficultyManager

class ChordIdentificationMode:
    # Mode 1: User identifies highlighted chord from multiple choice options
    
    def __init__(self, main_window, learning_ui):
        self.main_window = main_window
        self.learning_ui = learning_ui
        self.composer = ChordComposer()
        
        # Current question state
        self.current_question = None
        self.current_chord_notes = []
        self.correct_answer = None
        self.user_answer = None
        
    def start_question(self, difficulty):
        # Start a new chord identification question
        # Generate random chord based on difficulty
        root_note, chord_type = DifficultyManager.generate_random_chord(difficulty)
        
        # Generate the chord notes
        chord_name, chord_notes = self.composer.composeChord(root_note + "4", chord_type)
        
        # Store question data
        self.current_question = {
            "root_note": root_note,
            "chord_type": chord_type,
            "difficulty": difficulty
        }
        self.current_chord_notes = chord_notes
        self.correct_answer = f"{root_note} {chord_type}"
        self.user_answer = None
        
        # Generate answer choices
        choices = DifficultyManager.generate_answer_choices(
            (root_note, chord_type), difficulty
        )
        
        # Update UI
        self.learning_ui.update_question_display(
            "What chord is highlighted on the piano?",
            choices
        )
        
        # Highlight the chord and play it
        self.highlight_question_chord()
        self.play_question_chord()
        
        return True
    
    def highlight_question_chord(self):
        # Highlight the question chord on the piano
        # Reset all highlights first
        self.main_window.reset_all_piano_highlights()
        
        # Highlight chord notes in blue
        for note in self.current_chord_notes:
            # Use learning_ui method to get correct piano button (handles conversion)
            button = self.learning_ui.get_piano_button_for_note(note)
            if button:
                button.setStyleSheet("background-color: rgb(70, 130, 255); border: 2px solid rgb(50, 100, 200);")
    
    def play_question_chord(self):
        # Play the question chord sound
        for note in self.current_chord_notes:
            # Use learning_ui method to play note with conversion
            self.learning_ui.play_note_with_conversion(note, self.main_window.volume, 0)
    
    def replay_chord(self):
        # Replay the current question chord
        if self.current_chord_notes:
            self.play_question_chord()
    
    def submit_answer(self, selected_answer):
        # Process user's answer submission
        self.user_answer = selected_answer
        
        # Check if answer is correct
        is_correct = (selected_answer == self.correct_answer)
        
        # Show visual feedback
        if is_correct:
            self.show_correct_feedback()
        else:
            self.show_incorrect_feedback()
        
        # Calculate score
        score = self.calculate_score(is_correct)
        
        # Return result data
        return {
            "correct": is_correct,
            "user_answer": selected_answer,
            "correct_answer": self.correct_answer,
            "score": score
        }
    
    def show_correct_feedback(self):
        # Show green highlighting for correct answer
        for note in self.current_chord_notes:
            # Use learning_ui method to get correct piano button (handles conversion)
            button = self.learning_ui.get_piano_button_for_note(note)
            if button:
                button.setStyleSheet("background-color: rgb(80, 200, 80); border: 2px solid rgb(60, 150, 60);")
    
    def show_incorrect_feedback(self):
        # Show red highlighting for incorrect answer, then show correct answer
        # First show red (incorrect)
        for note in self.current_chord_notes:
            # Use learning_ui method to get correct piano button (handles conversion)
            button = self.learning_ui.get_piano_button_for_note(note)
            if button:
                button.setStyleSheet("background-color: rgb(255, 100, 100); border: 2px solid rgb(200, 80, 80);")
        
        # After 1 second, show correct answer in green
        QTimer.singleShot(1000, self.show_correct_feedback)
    
    def calculate_score(self, is_correct):
        # Calculate score based on correctness
        if not is_correct:
            return 0
        
        config = DifficultyManager.get_config(self.current_question["difficulty"])
        base_score = config["points_per_correct"]
        
        return base_score
    
    def show_answer(self):
        # Show the correct answer (hint feature)
        self.show_correct_feedback()
        return self.correct_answer
    
    def reset_piano_highlights(self):
        # Reset all piano highlights to original state
        self.main_window.reset_all_piano_highlights()
    
    def cleanup(self):
        # Clean up mode state
        self.reset_piano_highlights()
        self.current_question = None
        self.current_chord_notes = []
        self.correct_answer = None
        self.user_answer = None