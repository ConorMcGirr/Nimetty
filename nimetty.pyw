'''Last updated 05/08/2024 ¦¦¦ Go to end for TODO and DONE lists'''
import os, re, fileinput, sys, shutil, platform
import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Combobox
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
searchTerm = ''
newNames = {}
renameList = []
directoryPath = ''
appTitle = 'Nimetty'

# ================================== FUNCTIONS ==================================
def getInitialDir():
    if platform.system().lower() == 'linux' and 'settings.conf' in os.listdir():
        cwd = os.getcwd()
        print(f'Config file found: {cwd}\\settings.conf')
        with open(os.getcwd()+'/settings.conf', 'r') as settings:
            for line in settings:
                if re.search('^initialdir *\t*=', line, re.IGNORECASE):
                    initialDir = line.split('=')[-1]
                    print(f'initialdir setting found: {initialDir}')
                    return initialDir
                else:
                    return ''
    else:
        return ''

def writeInitialDir(newInitialDirectory):
    print(f'writeInitialDir function called with argument: {newInitialDirectory}')
    if 'settings.conf' in os.listdir():
        print('conf file found')
        for line in fileinput.input(os.getcwd()+'/settings.conf', inplace=1):
            if re.search('^initialdir *\t*=', line, re.IGNORECASE):
                replaceThis = line.split('=')[-1]
                line = line.replace(replaceThis, newInitialDirectory+'\n')
                sys.stdout.write(line)
    
def chooseDirectory():
    global directoryPath
    oldDirectoryPath = directoryPath
    initialDir = getInitialDir()
    print(f'initialDir is {initialDir}')
    if initialDir != '':
        directoryPath = askdirectory(initialdir=initialDir)
    else:
        directoryPath = askdirectory()
    if not directoryPath:
        directoryPath = oldDirectoryPath
        return
    writeInitialDir(directoryPath)
    window.title(f'{appTitle} - {directoryPath}')

def getFileList(directoryPath):
    fileList = []
    if includeFiles.get() and includeFolders.get():
        fileList = os.listdir(directoryPath)
    elif includeFiles.get() and not includeFolders.get():
        fileList = [file for file in os.listdir(directoryPath) if os.path.isfile(os.path.join(directoryPath, file))]
    elif not includeFiles.get() and includeFolders.get():
        fileList = [folder for folder in os.listdir(directoryPath) if os.path.isdir(os.path.join(directoryPath, folder))]
    fileList.sort(key=str.lower)
    return fileList

def open_file(dummy=None):
    chooseDirectory()
    fileList = getFileList(directoryPath)
    text = ''
    for file in fileList:
        text += file + '\n'
    overwriteTextBox(txtBox1, text)
    renameBtn.config(state='disabled')
    copyBtn.config(state='disabled')
    
def overwriteTextBox(textBox, text):
    textBox.config(state='normal')
    textBox.delete('1.0', tk.END)
    textBox.insert(tk.END, text)
    textBox.config(state='disabled')

def escapeRegex(searchTerm, regexCheck):
    if regexCheck == 0:
        searchTerm = re.escape(searchTerm)
        return searchTerm
    else:
        return searchTerm

def disableRenameBtns():
    renameBtn.config(state='disabled')
    copyBtn.config(state='disabled')

def search(dummy=None): # 'dummy' argument added to prevent error - "funcName() takes 0 positional arguments but 1 was given"
    global renameList
    global searchTerm
    if directoryPath == '':
        messagebox.showerror("Error", 'Search can\'t be done until a folder is chosen.')
        return
    fileList = getFileList(directoryPath)
    renameList = []
    searchTerm = searchBar.get()
    searchTerm = escapeRegex(searchTerm, useRegex.get())
    outputText = ''
    if caseSensitive.get() == 1:
        for filename in fileList:
            if re.search('.*' + searchTerm + '.*', filename):
                renameList.append(filename)
    else:
        for filename in fileList:
            if re.search('.*' + searchTerm + '.*', filename, re.IGNORECASE):
                renameList.append(filename)
    renameList.sort(key=str.lower)
    for filename in renameList:
        outputText += filename + '\n'
    overwriteTextBox(txtBox1, outputText)
    disableRenameBtns()

def generateNewNames(**kwargs):
    global newNames
    newNames = {}
    replacementString = replaceBar.get()
    outputText = ''
    renameMode = mode.get()
    for oldName in renameList:
        match renameMode:
            case "Replace with...":
                # To get case sensititve string subsititution to work, the search term has to be compiled
                searchTermCompiled = re.compile(searchTerm, re.IGNORECASE)
                newName = searchTermCompiled.sub(replacementString, oldName)
            case "Prefix with...":
                newName = f"{replacementString}{oldName}"
            case "Suffix with...":
                oldNameList = oldName.split('.')
                ext = oldNameList[-1]
                fName = '.'.join(oldNameList[0:-1])
                newName = f"{fName}{replacementString}.{ext}"
        newNames.update({oldName : newName})
        outputText += newName + '\n'
    overwriteTextBox(txtBox2, outputText)
    renameBtn.config(state='normal')
    copyBtn.config(state='normal')

def renameFiles(dummy=None):
    errorLog = ''
    if messagebox.askyesno('Warning!', 'Are you sure you want to directly edit the filenames?\nThis action can\'t be undone.'):
        for oldName, newName in newNames.items():
            try:
                os.rename(directoryPath+'/'+oldName, directoryPath+'/'+newName)
            except:
                errorLog += newName+'\n'
        if errorLog != '':
            errorLog = 'Error: Unable to change filenames to the following:\n' + errorLog
            errorLog += '\nCheck for duplicates in destination folder.'
            messagebox.showerror("Error", errorLog)

def copyFiles(dummy=None):
    errorLog=''
    for oldName, newName in newNames.items():
        try:
            shutil.copy2(directoryPath+'/'+oldName, directoryPath+'/'+newName)
        except:
            errorLog += newName+'\n'
    if errorLog != '':
        errorLog = 'Error: Unable to create the following files:\n\n' + errorLog
        errorLog += '\nCheck for duplicates in destination folder.'
        messagebox.showerror("Error", errorLog)

# ===================================== GUI =====================================
# Create window, configure
window = tk.Tk()
window.title(appTitle)
window.rowconfigure(2, minsize=200, weight=1)
window.columnconfigure(0, minsize=300, weight=1)
window.columnconfigure(2, minsize=300, weight=1)

# Create original filenames text box
scrollbar1 = tk.Scrollbar(window, orient='vertical')
txtBox1 = tk.Text(window, yscrollcommand=scrollbar1.set)
txtBox1.config(state='disabled')
scrollbar1.config(command=txtBox1.yview)
# Create edited filenames text box
scrollbar2 = tk.Scrollbar(window, orient='vertical')
txtBox2 = tk.Text(window, yscrollcommand=scrollbar2.set)
txtBox2.config(state='disabled')
scrollbar2.config(command=txtBox2.yview)
# Create frame 1
frame1 = tk.Frame(window)
chooseFolderBtn = tk.Button(frame1, text='Choose Folder', command=open_file)
chooseFolderBtn.bind('<Return>', open_file)
# Create check buttons & variable
includeFiles = tk.IntVar(value=1)
fileCheck = tk.Checkbutton(frame1, text='Files', variable=includeFiles, onvalue=1, offvalue=0, command=search)
includeFolders = tk.IntVar()
folderCheck = tk.Checkbutton(frame1, text='Folders', variable=includeFolders, onvalue=1, offvalue=0, command=search)
caseSensitive = tk.IntVar()
caseCheck = tk.Checkbutton(frame1, text='Case sensitive', variable=caseSensitive, onvalue=1, offvalue=0, command=search)
useRegex = tk.IntVar()
regexCheck = tk.Checkbutton(frame1, text='Regex', variable=useRegex, onvalue=1, offvalue=0, command=search)
# Create frame 2
frame2 = tk.Frame(window)
# Create search bar
searchBar = tk.Entry(frame2)
searchBar.bind('<Return>', search)
searchBtn = tk.Button(frame2, text='Search', command=search)
searchBtn.bind('<Return>', search)
# Create frame3
frame3 = tk.Frame(window)
# Create replace bar
replaceBar = tk.Entry(frame3)
replaceBar.bind('<Return>', generateNewNames)
replaceBtn = tk.Button(frame3, text='Preview', command=generateNewNames)
replaceBtn.bind('<Return>', generateNewNames)
# Create "mode" drop-down
mode = tk.StringVar() 
dropdownMode = Combobox(frame3, width = 13, textvariable = mode)
dropdownMode['values'] = ('Replace with...', 'Prefix with...', 'Suffix with...')
dropdownMode.current(0)
# Create frame4
frame4 = tk.Frame(window)
# Create Rename and Copy buttons
renameBtn = tk.Button(frame4, text='Rename files directly', command=renameFiles, state='disabled')
renameBtn.bind('<Return>', renameFiles)
copyBtn = tk.Button(frame4, text='Create copies with new names', command=copyFiles, state='disabled')
copyBtn.bind('<Return>', copyFiles)
# Grid
chooseFolderBtn.grid(row=0, column=0, sticky='w', padx=2, pady=5)
fileCheck.grid(row=0, column=1, padx=2, pady=5)
folderCheck.grid(row=0, column=2, padx=2, pady=5)
caseCheck.grid(row=0, column=3, padx=2, pady=5)
regexCheck.grid(row=0, column=4, padx=2, pady=5)
tk.Label(frame2, text='Search for...').grid(row=0, column=0, sticky='e')
searchBar.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky='ew')
searchBtn.grid(row=0, column=3, pady= 5, sticky='e')
txtBox1.grid(row=2, column=0, sticky='nsew')
scrollbar1.grid(row=2, column=1, sticky='nsew')
replaceBar.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
replaceBtn.grid(row=0, column=2)
#tk.Label(frame3, text='Replace with...').grid(row=0, column=0)
dropdownMode.grid(row=0, column=0)
txtBox2.grid(row=2, column=2, sticky='nsew')
scrollbar2.grid(row=2, column=3, sticky='nsew')
renameBtn.grid(row=1, column=1, padx=5, pady=5, sticky='e')
copyBtn.grid(row=1, column=2, padx=5, pady=5, sticky='e')
frame1.grid(row=0, column=0, sticky='ew') # sticky='ew' makes frame responsive inside grid
frame2.grid(row=1, column=0, sticky='ew')
frame2.grid_columnconfigure(1, weight=1)  # Make search bar repsonsive
frame3.grid(row=0, column=2, sticky='ew')
frame3.grid_columnconfigure(1, weight=1)
frame4.grid(row=1, column=0, columnspan=3, sticky='e')

window.mainloop()

# TO DO:
# - Save / read most recent directory in settings (only read when on linux) (needs tested on linux)

# DONE:
# - Added prefix and suffix modes
# - Bug fixed - Program quits when folder is changed (only when opened without terminal)
# - Bug fixed - Changes not being made to capitalisation e.g. NIMETTY won't rename to Nimetty
# - Bind ENTER key to all buttons
# - Correct the order in which tab cycles through items
# - Bug fixed - rename preview not working when Regex checked
# - Search refreshed whenever changes are made to check boxes
# - Add ENTER key functionality to search and replace bars
# - Escape regex characters
# - Fix bug - Pressing 'cancel' when choosing a folder when one is already chosen should keep already chosen folder
# - Produce error window when trying to search before folder is chosen
# - Don't allow files to be renamed or copied until preview is generated
# - Refresh file list every search
# - List files in existing file window alphabetically
# - Fix bug: Preview wont work unless case of search term matches that of string to be replaced
# - Include option to include / exclude directories
