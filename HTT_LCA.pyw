import sys
import u3                       #LabJackPython library supplied by LabJack
import xlsxwriter               #Used to edit and create Excel files
import Tkinter as tk            #Main graphics library
import tkMessageBox             #Tkinter library to make popup windows
import tkFileDialog             #Tkinter library to browse files
import matplotlib               #Graphics library for the plot
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import serial                   #Serial library to listen to the Xbee
import serial.tools.list_ports  #Serial library to list all the serial ports
import time
from datetime import datetime

#Analog input class, based on u3allio.py
class AIN:
    #Constructor
    def __init__(self):
        self.feedbackArguments = []
        
        #Configuring I/O
        d.configIO( FIOAnalog = (0xFF))
        d.getFeedback(u3.PortDirWrite(Direction = [0, 0, 0], WriteMask = [0, 0, 0]))
        
        self.feedbackArguments.append(u3.DAC0_8(Value = 125))
        self.feedbackArguments.append(u3.PortStateRead())
        for i in range(8):
            if (i < 4):
                self.feedbackArguments.append(u3.AIN(i, 31, QuickSample = 1, LongSettling = 0))
            else:
                self.feedbackArguments.append(u3.AIN(i, 30, QuickSample = 1, LongSettling = 0))
    
    #Getter function that simply returns the analog voltage of the specified channel
    def get_temp(self, sensNum):
        results = d.getFeedback(self.feedbackArguments)
        if(sensNum < 4):
            voltage = d.binaryToCalibratedAnalogVoltage(results[2+sensNum], isLowVoltage = False, isSingleEnded = True)
        else:
            voltage = 2.44 + d.binaryToCalibratedAnalogVoltage(results[2+sensNum], isLowVoltage = True, isSingleEnded = False)
        return voltage

#The main menu
class Menu:
    def __init__(self):
        #Setting up a new Tkinter window for the menu
        self.menuloop = tk.Tk()
        self.menuloop.title("Setup")
        self.menuloop.minsize(300, 220)
        self.menuloop.bind('<Return>', self.parseenter)                 #Allowing the use of the enter key to advance the menu
        self.menuloop.protocol('WM_DELETE_WINDOW', self.safe_exit_menu) #Adjusting the protocol for the 'x' to close the data safely
        self.menuloop.iconbitmap(r'C:\Python27\temp.ico')               #Assigning the icon to the window
        
        self.leninit = tk.IntVar()      #Length variable
        self.freqinit = tk.DoubleVar()  #Frequency variable
        self.pathinit = tk.StringVar()  #File path variable
        self.tempinit = tk.StringVar()  #Temperature unit variable
        
        #Setting the default values
        self.leninit.set(lenvar)
        self.freqinit.set(freqvar)
        self.pathinit.set(pathvar)
        self.tempinit.set(tempvar)
        
        #Tkinter label print length text
        lentext = tk.Label(self.menuloop, font = ("Courier", 10),
        text = "Enter the number of seconds to collect data:",
        wraplength = 200, padx = 2, pady = 2).grid(row = 1, column = 1)
        
        #Tkinter entry to get length value
        self.leninput = tk.Entry(self.menuloop, font = ("Courier", 15), width = 5, textvariable = self.leninit)
        self.leninput.grid(row = 1, column = 2)
        
        #Tkinter label print frequency text
        freqtext = tk.Label(self.menuloop, font = ("Courier", 10),
        text = "Enter the number of samples per second:",
        wraplength = 200, padx = 2, pady = 2).grid(row = 2, column = 1)
        
        #Tkinter entry to get frequency value
        self.freqinput = tk.Entry(self.menuloop, font = ("Courier", 15), width = 5, textvariable = self.freqinit)
        self.freqinput.grid(row = 2, column = 2)
        
        #Tkinter label print path text
        pathtext = tk.Label(self.menuloop, font = ("Courier", 10),
        text = "Choose the Excel file destination path:",
        wraplength = 200, padx = 2, pady = 2).grid(row = 3, column = 1)
        
        #Tkinter button to launch file browser
        browse = tk.Button(self.menuloop, text = "Browse", command = self.openfile,
        height = 2, width = 7).grid(row = 3, column = 2)
        
        #Tkinter label print units text
        temptext = tk.Label(self.menuloop, font = ("Courier", 10),
        text = "Choose temperature units:",
        wraplength = 200, padx = 2, pady = 2).grid(row = 4, column = 1)
        
        #Tkinter options menu to choose units
        self.tempinput = tk.OptionMenu(self.menuloop, self.tempinit, "C", "F")
        self.tempinput.grid(row = 4, column = 2)
        
        #Tkinter start button
        start = tk.Button(self.menuloop, text = "Start", command = self.menucheck,
        height = 2, width = 7).grid(row = 5, column = 1)
        
        self.menuloop.mainloop()
    
    #Function to map enter key to the start button
    def parseenter(self, event):
        self.menucheck()
    
    #Function to open file browser
    def openfile(self):
        self.pathinit.set(tkFileDialog.askdirectory(parent=self.menuloop,title='Choose a file'))
    
    #Function to check all the entered values
    #If everything is okay, values are copied and menu exits
    def menucheck(self):
        if ((int(self.leninput.get()) < 1) or (int(self.leninput.get()) > 7200)):
            tkMessageBox.showinfo("Error", "Please enter a valid number of seconds.\n(1-7200 sec.)")
        elif ((float(self.freqinput.get()) > 4) or (float(self.freqinput.get()) < 0.25)):
            tkMessageBox.showinfo("Error", "Please enter a valid number of samples per second.\n(0.25 - 4 samp/sec.)")
        elif str(self.pathinit.get()) == '':
            tkMessageBox.showinfo("Error", "Please choose a valid path.")
        else:
            global lenvar
            global freqvar
            global pathvar
            global tempvar
            lenvar = int(self.leninput.get())
            freqvar = float(self.freqinput.get())
            pathvar = str(self.pathinit.get()).replace('/', '\\') + '\TempData.xlsx'
            if (self.tempinit.get() == 'F'):
                tempvar = 1
            else:
                tempvar = 0
            
            #Close the Tkinter menu window
            self.menuloop.quit()
            self.menuloop.destroy()
    
    #Safely exit the menu
    def safe_exit_menu(self):
        #Close the Tkinter menu window
        self.menuloop.quit()
        self.menuloop.destroy()
        
        #Exit the program
        sys.exit(1)
    
#Function to setup the graph and excel file
def setup():
    
    #Declaring the variables as global so we can edit them.
    global background
    global labels
    global yvals
    
    #Make the graph as long as the sample
    ax.set_xlim(0, lenvar)
    
    #If we're in F, Y-range should be 600 degrees
    #If we're in C, Y-range should be 300 degrees
    if(tempvar):
        ax.set_ylim(0, 600)
    else:
        ax.set_ylim(0, 300)
    
    canvas = FigureCanvasTkAgg(fig, root)                           #Make the graph a figure in Tkinter
    canvas.show()
    canvas.get_tk_widget().grid(row = 1, column = 3, rowspan = 16)  #Placing the figure on Tk's grid
    
    #Copy the background into the global variable
    background = fig.canvas.copy_from_bbox(ax.bbox)
    
    #Label first column in excel as Time
    worksheet.write('A1', 'Time')
    
    #For loop to initialize excel sheet and graph
    for i in range(6):
        worksheet.write(chr(i+66)+'1', varnams[i])          #If i = 0, chr(66)+'1' = 'B1', used to iterate through columns in excel sheet
        labels.append(tk.Label(root, font = ("Courier", 15), fg = colors[i], text = '%s:\n%.2f %s' % (varnams[i], 0.0, varnams[tempvar+6]))) #Making the Tkinter labels to store numerical temperatures
        labels[i].grid(row = i+1, column = 1)               #Positioning the Tkinter labels
        yvals.append([])                                    #Adding an array for every measurement
    
    #Launching the main program
    updateWindow()
    
#Function that updates the graph and temperatures, and writes to the Excel file
def updateWindow():
    start = time.time() #Log the start time
    
    
    #Declaring the variables as global so we can edit them.
    global background
    global labels
    global yvals
    global sheetrow
    
    worksheet.write(chr(65)+str(sheetrow+1), datetime.now().strftime('%H:%M:%S.%f')[:-4]) #Put the current time in the first column
    xvals.append((sheetrow - 1)*period) #Log the current xval, based on the global sheetrow counter
    
    avgvals = [0, 0, 1000] #avgvals[0] is max average, avgvals[1] is total average, avgvals[2] is min average
    for i in range(4):
        j = 2*i
        temp1 = Eqs(0, a.get_temp(j))
        temp2 = Eqs(0, a.get_temp(j+1))
        avg = (temp1+temp2)/2
        avgvals[1] += avg
        if avg > avgvals[0]:
            avgvals[0] = avg
        if avg < avgvals[2]:
            avgvals[2] = avg
    avgvals[1] = avgvals[1]/4
    
    
    i = 0                   #Initialize couter to timeout request
    ser.write('n')          #Send char to request data
    line = ser.readline()   #Read the data from the LCA
    
    #Wait for the line from the LCA
    while (line == ''):
        line = ser.readline()   #Update the line
        
        #If i gets to 10, send char to request data again
        if (i > 10):
            ser.write('n')
            i = 0
        i += 1
    
    #Split the data by spaces
    data = line.split()
    
    tempdata = []                                       #Variable to store raw data
    tempdata.append((float(data[0])+float(data[1]))/2)  #The average of therm1 and therm2 (Temp1)
    tempdata.append((float(data[2])+float(data[3]))/2)  #The average of therm3 and therm4 (Temp2)
    tempdata.append(float(data[4]))                     #The internal therm (Internal)
    
    #Checks if the internal temperature is over temp
    Checkover(tempdata[2])
    
    #Variable to store plots
    plots = []
    
    for i in range(6):
        if i < 3:
            yvals[i].append(avgvals[i])
            worksheet.write(chr(i+66)+str(sheetrow+1), avgvals[i])
            labels[i].config(text = '%s:\n%.2f %s' % (varnams[i], avgvals[i], varnams[tempvar+6]))
            plots.append(ax.plot(xvals, yvals[i], color = colors[i])[0])
        else:
            j = i - 3
            yvals[i].append(Eqs(1, tempdata[j]))
            worksheet.write(chr(i+66)+str(sheetrow+1), Eqs(1, tempdata[j]))
            labels[i].config(text = '%s:\n%.2f %s' % (varnams[i], Eqs(1, tempdata[j]), varnams[tempvar+6]))
            plots.append(ax.plot(xvals, yvals[i], color = colors[i])[0])
    
    #Advancing the sheetrow
    sheetrow += 1
    
    #Restore the background and draw the new plots
    fig.canvas.restore_region(background)
    for i in range(6):
        ax.draw_artist(plots[i])
    fig.canvas.blit(ax.bbox)
    
    end = time.time() #Log the end time
    
    #end - start gives the time the loop took in seconds
    #If loop took more time than the period, pause for 1 ms before running loop again.
    #Otherwise wait for the period minus the loop time in miliseconds.
    if(period - (end - start) < 0):
        waitval = 1
    else:
        waitval = int(1000*(period - (end - start)))
    
    #If we have not taken the total number of samples, run the loop again
    #Otherwise print that data has finished collecting and save the excel file
    if sheetrow <= totalsamp:
        root.after(waitval, updateWindow)
    else:
        tkMessageBox.showinfo("Data collection completed.", "The labjack has finished collecting data for " + str(lenvar) + " seconds.")
        workbook.close()

#Function to map raw inputs to the correct calibration equation
def Eqs(eqselect, x):

    if eqselect == 0:               #Eqs of 0 is HTT mapping
        MV = (x - 1.25)*1000        #Turn the voltage into zero-centered milivolts
       
        #uTemp is the 6th order polynomial to map type T thermocouples to type K amplifier
        uTemp = (-0.17974) + (0.20855*MV) + (-5.1041*(10**-5)*(MV**2)) + (5.1153*(10**-8)*(MV**3)) + (-4.8922*(10**-11)*(MV**4)) + (2.3402*(10**-14)*(MV**5)) + (-4.1036*(10**-18)*(MV**6))
        
        #If tempvar = 1, we are working in F so we need to convert
        if(tempvar):
            uTemp = (uTemp*1.8) + 32
        return uTemp
        
    elif eqselect == 1:                     #Eqs of 1 is LCA mapping
        rawvolt = (float(x)/1023)*4.960     #Turn the digital value from LCA into voltage (note AREF constant)
        MV = (rawvolt - 1.25)*1000          #Turn the voltage into zero-centered milivolts
        
        #uTemp is the 6th order polynomial to map type T thermocouples to type K amplifier
        uTemp = (-0.17974) + (0.20855*MV) + (-5.1041*(10**-5)*(MV**2)) + (5.1153*(10**-8)*(MV**3)) + (-4.8922*(10**-11)*(MV**4)) + (2.3402*(10**-14)*(MV**5)) + (-4.1036*(10**-18)*(MV**6))
        
        #If tempvar = 1, we are working in F so we need to convert
        if(tempvar):
            uTemp = (uTemp*1.8) + 32
        return uTemp
        
    else:
        return x

#Function to check if the internal temperature is over certain thresholds
def Checkover(internal):
    internal = Eqs(1, internal)             #Turn raw data into temperature
    global alert                            #Declaring alert as global so we can edit it
    if(tempvar):                            #If tempvar = 1, we are working in F
        if(internal >= 95 and alert[0]):
            tkMessageBox.showinfo("Warning", "Internal temperature has reached 95 F. Remove LCA soon")
            alert[0] = 0 #Alert has been shown, don't show it again
        elif(internal >= 113 and alert[1]):
            tkMessageBox.showinfo("Warning!", "Internal temperature has reached 113 F! Internal temperature dangerous! Remove LCA now.")
            alert[1] = 0
        elif(internal >= 122 and alert[2]):
            tkMessageBox.showinfo("ALERT!", "Internal temperature has reached 122 F! Internal temperature CRITICAL! REMOVE LCA IMMEDIATELY!")
            alert[2] = 0
    else: #We are working in C
        if(internal >= 35 and alert[0]):
            tkMessageBox.showinfo("Warning", "Internal temperature has reached 35 C. Remove LCA soon")
            alert[0] = 0
        elif(internal >= 45 and alert[1]):
            tkMessageBox.showinfo("Warning!", "Internal temperature has reached 45 C! Internal temperature dangerous! Remove LCA now.")
            alert[1] = 0
        elif(internal >= 50 and alert[2]):
            tkMessageBox.showinfo("ALERT!", "Internal temperature has reached 50 C! Internal temperature CRITICAL! REMOVE LCA IMMEDIATELY!")
            alert[2] = 0

#Safely exit the program
def safe_exit():
    #If we're still taking data, close the workbook now
    if(sheetrow <= totalsamp):
        workbook.close()
    
    #Close the Tkinter window
    root.quit()
    root.destroy()
    
    #Exit the program
    sys.exit(1)

#Variables to store menu settings, with default values
lenvar = 1
freqvar = 1
pathvar = ''
tempvar = 'C'

#Running the menu class
Menu()

#Setting up a new Tkinter window for the graph
root = tk.Tk()                                  #Creating the root
root.title("HTT and LCA")                       #Setting the title of the window
root.minsize(725, 500)                          #Setting the minimum size of the window
root.protocol('WM_DELETE_WINDOW', safe_exit)    #Adjusting the protocol for the 'x' to close the data safely
root.iconbitmap(r'C:\Python27\temp.ico')        #Assigning the icon to the window

#Global vars to be accesed by multiple functions
xvals = []                                      #Stores xvals of graph
yvals = []                                      #Stores yvals of graph
labels = []                                     #Stores the tkinter labels that show the temperatures
sheetrow = 1                                    #Global variable to keep track of which row to write to on the excel sheet
varnams = ['Max.', 'Avg.', 'Min.', 'Temp1', 'Temp2', 'Internal', 'C', 'F'] #The names of the variables to print
alert = [1, 1, 1]                               #Keep track of when we have triggered each level or alert so we alert multiple times
totalsamp = int(lenvar*freqvar)+1               #The total number of samples to collect
colors = ['red', 'darkgreen', 'blue', 'cyan', 'magenta', 'green'] #The colors on the graph
period = 1/freqvar

#Initializing the LabJack U3
d = u3.U3()

#Initializing the analog input class
a = AIN()

#Creating the plot
fig, ax = plt.subplots(1, 1)
background = 0 #Global variable to store the background of the graph

#Initializing the Excel library and creating new file
workbook = xlsxwriter.Workbook(pathvar)
worksheet = workbook.add_worksheet()

#Finding the Xbee Explorer port number
xbeeport = ''
ports = list(serial.tools.list_ports.comports())

#Searching for the PID of the Explorer
for p in ports:
    if "PID=0403:6015" in p[2]:
        xbeeport = p[0]

#Opening communications with the Xbee
ser = serial.Serial(xbeeport, 9600, timeout = 0.1)

#Setting up the plot and Excel file
setup()

#Running the graph loop
root.mainloop()