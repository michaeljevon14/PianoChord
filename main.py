import sys
from PyQt5 import QtWidgets
from piano_ui import Ui_MainWindow

if __name__ == "__main__":
    # Create a custom MainWindow class that extends QMainWindow
    class PianoMainWindow(QtWidgets.QMainWindow):
        def closeEvent(self, event):
            # Check if learning mode is active with a session
            if (hasattr(self.ui, 'learning_mode_active') and 
                self.ui.learning_mode_active and 
                hasattr(self.ui, 'learning_ui') and 
                self.ui.learning_ui and 
                self.ui.learning_ui.session_active):
                
                # Show warning dialog
                reply = QtWidgets.QMessageBox.question(
                    self,
                    "Session In Progress",
                    "You have a learning session in progress.\n\n"
                    "Are you sure you want to exit?\n"
                    "Your current progress will be lost.",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.No
                )
                
                if reply == QtWidgets.QMessageBox.No:
                    event.ignore()  # Don't close the window
                    return
            
            # Clean up FluidSynth
            if hasattr(self.ui, 'fs'):
                self.ui.fs.delete()
            
            # Close all child windows
            if hasattr(self.ui, 'chordWindow') and self.ui.chordWindow:
                self.ui.chordWindow.close()
            
            if hasattr(self.ui, 'progressionWindow') and self.ui.progressionWindow:
                self.ui.progressionWindow.close()
            
            # Accept the close event
            event.accept()
    
    # Initialize the application
    app = QtWidgets.QApplication(sys.argv)

    # Main window implementation with adjusted size
    MainWindow = PianoMainWindow()
    MainWindow.setFixedSize(640, 420)  # Set fixed window size for the piano layout
    
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.ui = ui  # Store a reference to the UI for use in closeEvent
    MainWindow.show()
    sys.exit(app.exec_())