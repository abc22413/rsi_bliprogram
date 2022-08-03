# Features
## Motor Control
### Manual movement
4 buttons (up, down, left, right) allow for the user to translate the stage along the anterior-posterior axis (front-back) and lateral-medial axis (left-right)

### Calibration
Contact switches allow for centering in the front-back and left-right axis. The system counts the steps needed to traverse the span from activating the contact switch on one end to the other and then centers itself. A calibration allows the system to specify origin.

### Position Callouts
After a calibration is performed, the system initializes origin at the calibrated positions. The axes are positive to the front and right. The minimum step is 8mm (thread) / 200 (stepper motors are set to 200steps/rev) = 0.04mm.

### Translate by
Specify a distance to translate the stage by in either axis; the system takes the value to the nearest 0.04mm.

### Translate to
After calibration establishes an origin, the system can also translate to a given position in the 2 axes.

### Focus
The system allows for the focusing of a lens through the use of an external motor with in-built hardware protection from overactuating the focusing mechanism.

## Coding Features
### Logging
Logging is implemented to enable debugging and performance monitoring in the future.

### Persistence of calibration
After a calibration is performed, the position of stage on shutdown is persisted to remove the need for calibration each tiem the system is started up.

# Details on Operation
On first downloading the code, you will need to calibrate the system as position is NaN. Simply press "translate to" and the system will prompt for the calibration of both axes on its own.

The pin assignments are available in gui_driver.py. The hardware motor drivers are 200steps/rev for the translational motors and 800steps/rev for the focusing mechanism motor.

# Details on Code
The GUI setup and mainloop code are in gui_driver.py under one function. I'm sorry for the poor code formatting as the software was written in a few hours due to time constraints, I'll be refactoring it sometime.

main.py initializes logging and runs the GUI loop under gui_driver.py
