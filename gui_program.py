#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tkinter import simpledialog, messagebox
from tkinter import *
import math
import serial.tools.list_ports
import pyfirmata
from admin import *

def run_app(arduino_port="COM9"):
    #TODO: Logging messages
    #TODO: Switch diagnostic

    '''MOTOR SETUP'''
    global UP_MOVE_N; UP_MOVE_N = 1
    global UP_MOVE_DELAY; UP_MOVE_DELAY = 50
    global LEFT_MOVE_N; LEFT_MOVE_N = 1
    global LEFT_MOVE_DELAY; LEFT_MOVE_DELAY = 50
    global RIGHT_MOVE_N; RIGHT_MOVE_N = 1
    global RIGHT_MOVE_DELAY; RIGHT_MOVE_DELAY = 50
    global DOWN_MOVE_N; DOWN_MOVE_N = 1
    global DOWN_MOVE_DELAY; DOWN_MOVE_DELAY = 50
    global CAMERA_MOVE_DELAY; CAMERA_MOVE_DELAY=20
    global CAMERA_MOVE_N; CAMERA_MOVE_N = 1

    global THREAD; THREAD = 8
    global STEPS; STEPS = 200

    '''GUI SETUP'''
    global SETTINGS
    SETTINGS = get_settings()
    logging.debug("User settings successfully loaded.")

    '''ARDUINO SETUP'''
    #Pin assignments
    # Motor A and B (lateral-medial translation)
    pul = 52
    dir = 53
    # Motor C (anterior-posterior translation)
    c_pul = 35
    c_dir = 34
    # Motor D (Camera lens zoom)
    d_pul = 29
    d_dir = 28
    # Switches on motor A unit
    a_prox = 51
    a_dist = 50
    # Switches on motor B unit
    b_prox = 45
    b_dist = 44
    # Switches on motor C unit
    c_prox = 36
    c_dist = 37

    #Establish communications with board
    board = pyfirmata.ArduinoMega(arduino_port)
    logging.debug("Communication with Arduino established on port {}.".format(arduino_port))

    #Assign input pins
    a_prox_input = board.digital[a_prox]
    a_dist_input = board.digital[a_dist]
    b_prox_input = board.digital[b_prox]
    b_dist_input = board.digital[b_dist]
    c_prox_input = board.digital[c_prox]
    c_dist_input = board.digital[c_dist]
    for input_pin in [a_prox_input, a_dist_input, b_prox_input, b_dist_input, c_prox_input, c_dist_input]:
        input_pin.mode = pyfirmata.INPUT
    logging.debug("Input pins assigned.")

    #Assign output pins
    pul_output = board.digital[pul]
    dir_output = board.digital[dir]
    c_pul_output = board.digital[c_pul]
    c_dir_output = board.digital[c_dir]
    d_pul_output = board.digital[d_pul]
    d_dir_output = board.digital[d_dir]
    for output_pin in [pul_output, dir_output, c_pul_output, c_dir_output, d_pul_output, d_dir_output]:
        output_pin.mode = pyfirmata.OUTPUT
    dir_output.write(1) #Initialise direction pin HIGH (distal motion)
    c_dir_output.write(1) #Initialise direction pin HIGH (distal motion)
    d_dir_output.write(1) #Initialise direction pin HIGH ()
    logging.debug("Output pins assigned.")

    #Start iterator for data input stream
    it = pyfirmata.util.Iterator(board)
    it.start()

    logging.debug("Arduino setup done.")

    '''GUI window'''
    root = Tk()
    root.geometry("300x500")
    root.title("Primate BLI System 1.0")
    logging.debug("GUI window successfully made.")

    '''GUI-specific globals'''
    #KIV for user protection
    global CALIBRATION_ON; CALIBRATION_ON = False
    #Counter for stepper steps in left-right axis
    global SIDE_STEPS; SIDE_STEPS = SETTINGS["Startup"]["X"]; print(SIDE_STEPS)
    global SIDE_STEPS_STR; SIDE_STEPS_STR = StringVar()
    def update_side_steps_str():
        global SIDE_STEPS; global SIDE_STEPS_STR
        SIDE_STEPS_STR.set("Lateral-Medial Position (X): "+("%.2f"%(SIDE_STEPS*THREAD/STEPS))+" mm\n (0 indicates calibrated center; positive to right)")
    update_side_steps_str()

    #Counter for stepper steps in front-back axis
    global VERT_STEPS; VERT_STEPS = SETTINGS["Startup"]["Y"]; print(VERT_STEPS)
    global VERT_STEPS_STR; VERT_STEPS_STR = StringVar(); 
    def update_vert_steps_str():
        global VERT_STEPS; global VERT_STEPS_STR
        VERT_STEPS_STR.set("Anterior-Posterior Position (Y): "+("%.2f"%(VERT_STEPS*THREAD/STEPS))+" mm\n (0 indicates calibrated center; positive to front)")
    update_vert_steps_str()

    '''MOTOR HELPER FUNCTIONS'''
    #Moves translational motor n steps in dir pin = direction. side = side motors / front-back
    #dir = HIGH represents distal motion from motor
    def move_motor(side=True, n=1, direction=-1):
        if side == True:
            global SIDE_STEPS
            if direction!=-1 and direction in [0,1]:
                dir_output.write(direction)
            for _ in range(n):
                pul_output.write(0)
                pul_output.write(1)
                if math.isnan(SIDE_STEPS)==False:
                    SIDE_STEPS+=1 if direction==1 else -1
                    update_side_steps_str()
        elif side == False:
            global VERT_STEPS
            if direction!=-1 and direction in [0,1]:
                c_dir_output.write(direction)
            for _ in range(n):
                c_pul_output.write(0)
                c_pul_output.write(1)
                if math.isnan(VERT_STEPS)==False:
                    VERT_STEPS+=1 if direction==0 else -1
                    update_vert_steps_str()

    #Move camera motor (n) steps in given direction
    def move_camera(n=1, direction=1):
        d_dir_output.write(direction)
        for _ in range(n):
            d_pul_output.write(1)
            d_pul_output.write(0)

    def center_side_motors():
        #Hardware switches of A have been calibrated to actuate before B's
        #Since stages of motors A and B are linked mechanically by wooden rigidbody, synchronize using A's switches
        try:
            #Disable other buttons to prevent stray inputs from creating race condition
            for child in root.winfo_children():
                if type(child)==type(Button):
                    child.configure(state="disable")
            #Move motor flush to the right
            while a_dist_input.read()!=1:
                move_motor(direction=1)
            span = 0
            #Move motor flush to the left and get span
            while a_prox_input.read()!=1:
                move_motor(direction=0)
                span+=1
            #Go to center
            for _ in range(span//2):
                move_motor(direction=1)
            global SIDE_STEPS; SIDE_STEPS=0
        except:
            pass
        finally:
            #Make sure widgets are re-enabled regardless, else GUI is useless
            for child in root.winfo_children():
                if type(child)==type(Button):
                    child.configure(state="normal")
                update_side_steps_str()
    
    def center_vert_motors():
        #Hardware switches of A have been calibrated to actuate before B's
        #Since stages of motors A and B are linked mechanically by wooden rigidbody, synchronize using A's switches
        try:
            #Disable other buttons to prevent stray inputs from creating race condition
            for child in root.winfo_children():
                if type(child)==type(Button):
                    child.configure(state="disable")
            #Move motor flush to the right
            while c_dist_input.read()!=1:
                move_motor(side=False, direction=1)
            span = 0
            #Move motor flush to the left and get span
            while c_prox_input.read()!=1:
                move_motor(side=False, direction=0)
                span+=1
            #Go to center
            for _ in range(span//2):
                move_motor(side=False, direction=1)
            global VERT_STEPS; VERT_STEPS=0
        except:
            pass
        finally:
            #Make sure widgets are re-enabled regardless, else GUI is useless
            for child in root.winfo_children():
                if type(child)==type(Button):
                    child.configure(state="normal")
                update_vert_steps_str()

    '''
    LAYOUT

    up_btn
    left_btn <space> right_btn
    down_btn
    label_latmed <callout_latmed> label_latmed_explanation
    label_antpos <callout_antpos> label_antpos_explanation
    center_latmed_btn
    center_antpos_btn
    '''

    #Workaround for sizing in pixels
    pixel = PhotoImage(width=1, height=1)

    '''Row 1'''
    #Up button
    def up_button_pressed(event):
        logging.debug("Up Pressed")
        up_button_move_motor()
    def up_button_released(event):
        global up_move_job_id
        root.after_cancel(up_move_job_id)
        logging.debug("Up Released")
    def up_button_move_motor():
        global up_move_job_id
        global UP_MOVE_N
        global UP_MOVE_DELAY
        move_motor(side=False, n=UP_MOVE_N, direction=0)
        up_move_job_id = root.after(UP_MOVE_DELAY, up_button_move_motor)
    up_button = Button(root, text="Up", relief=RIDGE, image=pixel, compound="c", width=40, height=60)
    up_button.bind("Button-1")
    up_button.bind("<Button-1>", up_button_pressed)
    up_button.bind("<ButtonRelease-1>", up_button_released)
    up_button.place(x=125, y=20)

    '''Row 2'''
    #Left Button
    def left_button_pressed(event):
        logging.debug("Left Pressed")
        left_button_move_motor()
    def left_button_released(event):
        global left_move_job_id
        root.after_cancel(left_move_job_id)
        logging.debug("Left Released")
    def left_button_move_motor():
        global left_move_job_id
        global LEFT_MOVE_N
        global LEFT_MOVE_DELAY
        move_motor(side=True, n=LEFT_MOVE_N, direction=0)
        left_move_job_id = root.after(LEFT_MOVE_DELAY, left_button_move_motor)
    left_button = Button(text="Left", relief=RIDGE, image=pixel, compound="c", width=60, height=40)
    left_button.bind("Button-1")
    left_button.bind("<Button-1>", left_button_pressed)
    left_button.bind("<ButtonRelease-1>", left_button_released)
    left_button.place(x=50, y=90)

    #Right Button
    def right_button_pressed(event):
        logging.debug("Right Pressed")
        right_button_move_motor()
    def right_button_released(event):
        global right_move_job_id
        root.after_cancel(right_move_job_id)
        logging.debug("Right Released")
    def right_button_move_motor():
        global right_move_job_id
        global RIGHT_MOVE_N
        global RIGHT_MOVE_DELAY
        move_motor(side=True, n=RIGHT_MOVE_N, direction=1)
        right_move_job_id = root.after(RIGHT_MOVE_DELAY, right_button_move_motor)
    right_button = Button(text="Right", relief=RIDGE, image=pixel, compound="c", width=60, height=40)
    right_button.bind("Button-1")
    right_button.bind("<Button-1>", right_button_pressed)
    right_button.bind("<ButtonRelease-1>", right_button_released)
    right_button.place(x=180, y=90)

    '''Row 3'''
    #Down Button
    def down_button_pressed(event):
        logging.debug("Down Pressed")
        down_button_move_motor()
    def down_button_released(event):
        global down_move_job_id
        root.after_cancel(down_move_job_id)
        logging.debug("Down Released")
    def down_button_move_motor():
        global down_move_job_id
        global DOWN_MOVE_N
        global DOWN_MOVE_DELAY
        move_motor(side=False, n=DOWN_MOVE_N, direction=1)
        down_move_job_id = root.after(DOWN_MOVE_DELAY, down_button_move_motor)
    down_button = Button(text="Down", relief=RIDGE, image=pixel, compound="c", width=40, height=60)
    down_button.bind("Button-1")
    down_button.bind("<Button-1>", down_button_pressed)
    down_button.bind("<ButtonRelease-1>", down_button_released)
    down_button.place(x=125, y=140)

    '''Row 4'''
    #Side position indicator
    side_label = Label(textvariable=SIDE_STEPS_STR)
    side_label.place(x=20, y=220)

    '''Row 5'''
    #Side position indicator
    vert_label = Label(textvariable=VERT_STEPS_STR)
    vert_label.place(x=20, y=270)

    '''Row 6'''
    #Go to set position
    def goto_button_pressed():
        global SIDE_STEPS; global VERT_STEPS
        if math.isnan(SIDE_STEPS) or math.isnan(VERT_STEPS):
            messagebox.showwarning("Calibration Required", "You will need to calibrate the system before proceeding")
            if messagebox.askyesnocancel("Calibration Required", "Proceed to calibrate BLI system?")!=True:
                return
            center_side_motors()
            center_vert_motors()

        x_posn = simpledialog.askfloat("2D Goto", "Enter X position in mm from origin (to nearest {}mm). Rightwards is positive".format(THREAD/STEPS))
        y_posn = simpledialog.askfloat("2D Goto", "Enter Y position in mm from origin (to nearest {}mm). Forwards is positive".format(THREAD/STEPS))

        #Round input to hardware's precision and get required translation from position
        x_steps = int(x_posn/(THREAD/STEPS)) - SIDE_STEPS
        y_steps = int(y_posn/(THREAD/STEPS)) - VERT_STEPS

        #Move motor
        for _ in range(abs(x_steps)):
            #direction=1 corresponds to distal --> rightwards motion
            move_motor(side=True, direction=0 if x_steps<0 else 1)
        for _ in range(abs(y_steps)):
            #direction=1 corresponds to distal -->backwards motion
            move_motor(side=False, direction=1 if y_steps<0 else 0)

    goto_button = Button(text="Go to Position", relief=RIDGE, image=pixel, compound="c", width=120, height=25, command=goto_button_pressed)
    goto_button.place(x=10, y=320)

    #Move by
    def moveby_button_pressed():
        #Get values to move by
        x_trans = simpledialog.askfloat("2D Translation", "Enter X translation distance in mm (to nearest {}mm)".format(THREAD/STEPS))
        y_trans = simpledialog.askfloat("2D Translation", "Enter Y translation distance in mm (to nearest {}mm)".format(THREAD/STEPS))
        
        #Round to hardware's precision
        x_steps = int(x_trans/(THREAD/STEPS))
        y_steps = int(y_trans/(THREAD/STEPS))

        #Move motor
        for _ in range(abs(x_steps)):
            #direction=1 corresponds to distal --> rightwards motion
            move_motor(side=True, direction=0 if x_trans<0 else 1)
        for _ in range(abs(y_steps)):
            #direction=1 corresponds to distal -->backwards motion
            move_motor(side=False, direction=1 if y_trans<0 else 0)
        
    moveby_button = Button(text="Move by Amount", relief=RIDGE, image=pixel, compound="c", width=120, height=25, command=moveby_button_pressed)
    moveby_button.place(x=160, y=320)

    '''Row 7'''
    #Center lateral-medial axis
    def center_latmed_button_pressed():
        messagebox.showwarning("Warning", "Remove animal from cradle. Ensure no obstructions in the path of the motor")
        center_side_motors()
    center_latmed_button = Button(text="Center left-right motors", relief=RIDGE, image=pixel, compound="c", width=140, height=25, command=center_latmed_button_pressed)
    center_latmed_button.place(x=70, y=360)

    '''Row 8'''
    #Center anterior-posterior axis
    def center_antopos_button_pressed():
        messagebox.showwarning("Warning", "Remove animal from cradle. Ensure no obstructions in the path of the motor")
        center_vert_motors()
    center_antpos_button = Button(text="Center front-back motors", relief=RIDGE, image=pixel, compound="c", width=140, height=25, command = center_antopos_button_pressed)
    center_antpos_button.place(x=70, y=400)

    '''Row 9'''
    #Zoom in button
    def zoomin_button_pressed(event):
        logging.debug("Zoom in button Pressed")
        zoomin_button_move_motor()
    def zoomin_button_released(event):
        global zoomin_move_job_id
        root.after_cancel(zoomin_move_job_id)
        logging.debug("Zoom in button Released")
    def zoomin_button_move_motor():
        global zoomin_move_job_id
        global CAMERA_MOVE_N
        global CAMERA_MOVE_DELAY
        move_camera(n=CAMERA_MOVE_N, direction=1)
        zoomin_move_job_id = root.after(CAMERA_MOVE_DELAY, zoomin_button_move_motor)
    zoomin_button = Button(text="Focus In", relief=RIDGE, image=pixel, compound="c", width=120, height=25)
    zoomin_button.bind("Button-1")
    zoomin_button.bind("<Button-1>", zoomin_button_pressed)
    zoomin_button.bind("<ButtonRelease-1>", zoomin_button_released)
    zoomin_button.place(x=10, y=440)

    #Zoom out button
    def zoomout_button_pressed(event):
        logging.debug("Zoom out button Pressed")
        zoomout_button_move_motor()
    def zoomout_button_released(event):
        global zoomout_move_job_id
        root.after_cancel(zoomout_move_job_id)
        logging.debug("Zoom out button Released")
    def zoomout_button_move_motor():
        global zoomout_move_job_id
        global CAMERA_MOVE_N
        global CAMERA_MOVE_DELAY
        move_camera(n=CAMERA_MOVE_N, direction=0)
        zoomout_move_job_id = root.after(CAMERA_MOVE_DELAY, zoomout_button_move_motor)
    zoomout_button = Button(text="Focus Out", relief=RIDGE, image=pixel, compound="c", width=120, height=25)
    zoomout_button.bind("Button-1")
    zoomout_button.bind("<Button-1>", zoomout_button_pressed)
    zoomout_button.bind("<ButtonRelease-1>", zoomout_button_released)
    zoomout_button.place(x=160, y=440)

    '''MENU'''
    menubar = Menu(root)

    #Settings
    settings = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Settings", menu=settings)

    #Change logging level (can be used for diagnostics of machine)
    def change_loglevel():
        changeloglevel = None
        while changeloglevel == None:
            messagebox.showinfo("Instructions", "Type only 'DEBUG', 'WARNING'," +
                                " 'ERROR' or 'CRITICAL' into the text field.", parent=root)
            temp_changeloglevel = simpledialog.askstring("Change Loglevel", "Change" +
                                                            " Loglevel to:")
            if temp_changeloglevel:
                temp_changeloglevel = temp_changeloglevel.replace(" ", "").upper()
                if temp_changeloglevel in ['DEBUG', 'WARNING',
                                            'ERROR', 'CRITICAL']:
                    changeloglevel = temp_changeloglevel
                    break
        SETTINGS["Loglevel"] = changeloglevel
        with open("appdata/settings", "wb") as f:
            pickle.dump(SETTINGS, f)
        root.quit()
    multiloglevel = settings.add_command(label="Change Loglevel", command=change_loglevel)

    root.config(menu=menubar)

    #Modify window closing behavior to ensure steps are saved to settings
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            SETTINGS["Startup"]["X"] = SIDE_STEPS
            SETTINGS["Startup"]["Y"] = VERT_STEPS
            with open("appdata/settings", "wb") as f:
                        pickle.dump(SETTINGS, f)
            root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)

    '''At end of each loop'''
    root.mainloop()