import random
from note_converter import NoteConverter

class DifficultyManager:
    # Manages difficulty settings and question generation parameters
    
    DIFFICULTY_CONFIG = {
        "easy": {
            "root_notes": ["C", "F", "G", "A", "D", "E"],
            "chord_types": ["major", "minor"],
            "questions_per_session": 5,
            "answer_choices": 4,
            "points_per_correct": 10,
        },
        "medium": {
            "root_notes": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
            "chord_types": ["major", "minor", "diminished"],
            "questions_per_session": 8,
            "answer_choices": 4,
            "points_per_correct": 15,
        }
    }
    
    @classmethod
    def get_config(cls, difficulty):
        # Get configuration for a difficulty level
        return cls.DIFFICULTY_CONFIG.get(difficulty, cls.DIFFICULTY_CONFIG["easy"])
    
    @classmethod
    def generate_random_chord(cls, difficulty):
        # Generate a random chord based on difficulty settings
        config = cls.get_config(difficulty)
        root_note = random.choice(config["root_notes"])
        chord_type = random.choice(config["chord_types"])

        # For diminished chords, convert to appropriate flat notation
        if chord_type == "diminished":
            root_note = NoteConverter.convert_for_diminished_chord(root_note)

        return root_note, chord_type

    @classmethod
    def generate_answer_choices(cls, correct_answer, difficulty):
        # Generate multiple choice options including the correct answer
        config = cls.get_config(difficulty)
        root_note, chord_type = correct_answer
        
        # Start with correct answer
        choices = [f"{root_note} {chord_type}"]
        
        # Generate wrong answers
        while len(choices) < config["answer_choices"]:
            # Generate random wrong answer
            wrong_root = random.choice(config["root_notes"])
            wrong_type = random.choice(config["chord_types"])

            # Apply appropriate notation for the wrong answer too
            if wrong_type == "diminished":
                wrong_root = NoteConverter.convert_for_diminished_chord(wrong_root)

            wrong_answer = f"{wrong_root} {wrong_type}"
            
            # Don't add duplicates or the correct answer
            if wrong_answer not in choices:
                choices.append(wrong_answer)
        
        # Shuffle so correct answer isn't always first
        random.shuffle(choices)
        return choices
    
    @classmethod
    def get_available_difficulties(cls):
        # Get list of available difficulty levels
        return list(cls.DIFFICULTY_CONFIG.keys())