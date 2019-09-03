#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import subprocess
import os
import random
import xml.etree.ElementTree as ET
import math
import configparser
import pdfkit
from tkinterhtml import HtmlFrame
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfile, asksaveasfilename

class PaneConfig:

    def __init__(self, root, mainWindow):
        self.root = root
        self.mainWindow = mainWindow
        self.paneWidth = DoubleVar(self.root, 17.0)
        self.paneHeight = DoubleVar(self.root, 17.0)
        self.bulletSize = DoubleVar(self.root, 4.5)
        self.gridColumns = IntVar(self.root, 17)
        self.gridRows = IntVar(self.root, 17)
        self.valuesMin = IntVar(self.root, 0)
        self.valuesMax = IntVar(self.root, 25)
        self.valuesSteps = IntVar(self.root, 5)
        self.scoringOptions = [('Kleinsten Wert', 'min'), ('Größten Wert', 'max'), ('Meiste Abdeckung', 'cov'), ('Summe aller Werte', 'sum')]
        self.scoring = StringVar(self.root, self.scoringOptions[-1][1])
        self.teamScoringOptions = [('Beste Ergebnisse', 'best'), ('Schlechteste Ergebnisse', 'worst'), ('Durchschnitt', 'average'), ('Alle', 'all')]
        self.teamScoring = StringVar(self.root, self.teamScoringOptions[0][1])
        self.teamOptions = [('keine Teams', 'none'), ('Teams aus Vereinen', 'club'), ('Teams auf Personenebene', 'person'), ('Teams auf Scheibenebene', 'pane')]
        self.team = StringVar(self.root, self.teamOptions[0][1])
        self.separateGender = IntVar(self.root, 0)
        self.separateAgeClass = IntVar(self.root, 0)
        self.configFile = StringVar(self.root, '')
        self.currentTab = 0
        self.values = []
        self.horizontal = []
        self.vertical = []

    def loadPane(self):
        config = configparser.ConfigParser()
        filename = askopenfilename(initialdir = os.getcwd(), parent = self.mainWindow.root, title = "Datei auswählen", filetypes = [("ini","*.ini")])
        self.configFile.set(filename)
        config.read(filename)
        self.paneWidth.set(float(config['Settings']['paneWidth']))
        self.paneHeight.set(float(config['Settings']['paneHeight']))
        self.bulletSize.set(float(config['Settings']['bulletSize']))
        self.gridColumns.set(int(config['Settings']['gridColumns']))
        self.gridRows.set(int(config['Settings']['gridRows']))
        self.valuesMin.set(int(config['Settings']['valuesMin']))
        self.valuesMax.set(int(config['Settings']['valuesMax']))
        self.valuesSteps.set(int(config['Settings']['valuesSteps']))
        values = config['Pane']['values']
        values = values.split("/")
        for i in range(len(values)):
            values[i] = [int(x) for x in values[i].split(",")]
        self.values = values
        self.calculateGrid()

    def createPane(self):
        self.values = []
        for i in range(self.gridRows.get()):
            val = []
            for j in range(self.gridColumns.get()):
                val.append(random.randrange(self.valuesMin.get(), self.valuesMax.get(), self.valuesSteps.get()))
            self.values.append(val)
        self.calculateGrid()
        self.configFile.set(os.getcwd() + "/" + str(datetime.datetime.now()).replace(":", "-").replace(" ", "-") + ".ini")
        self.savePane()

    def savePane(self):
        filename = self.configFile.get()
        if (len(filename) == 0):
            filename = os.getcwd() + "/" + str(datetime.datetime.now()).replace(":", "-").replace(" ", "-") + ".ini"
            self.configFile.set(filename)
        cfgfile = open(filename, 'w')
        config = configparser.ConfigParser()
        config.add_section('Settings')
        config.set('Settings', 'paneWidth', str(self.paneWidth.get()))
        config.set('Settings', 'paneHeight', str(self.paneHeight.get()))
        config.set('Settings', 'bulletSize', str(self.bulletSize.get()))
        config.set('Settings', 'gridColumns', str(self.gridColumns.get()))
        config.set('Settings', 'gridRows', str(self.gridRows.get()))
        config.set('Settings', 'valuesMin', str(self.valuesMin.get()))
        config.set('Settings', 'valuesMax', str(self.valuesMax.get()))
        config.set('Settings', 'valuesSteps', str(self.valuesSteps.get()))
        config.add_section('Pane')
        values = ''
        for element in self.values:
            values = values + ','.join(str(x) for x in element) + "/"
        values = values[:-1]
        config.set('Pane', 'values', values)
        config.write(cfgfile)
        cfgfile.close()

    def calculateGrid(self):
        self.horizontal = []
        self.horizontalStep = self.paneWidth.get() * 10 / self.gridColumns.get()
        for i in range(self.gridColumns.get() + 1):
            self.horizontal.append(i * self.horizontalStep - (self.paneWidth.get() * 10 / 2))
        self.vertical = []
        self.verticalStep = self.paneHeight.get() * 10 / self.gridRows.get()
        for i in range(self.gridRows.get() + 1):
            self.vertical.append((self.paneHeight.get() * 10 / 2) - i * self.verticalStep) 

class Results:

    def __init__(self, root, mainWindow):
        self.root = root
        self.mainWindow = mainWindow
        self.config = self.mainWindow.config
        self.resultFile = StringVar(self.root, '')
        self.shooterCount = StringVar(self.root, '')
        self.results = []

    def loadResult(self):
        initdir = os.getcwd()
        if (os.path.exists("/var/shootmaster/ERGEBNIS/XML")):
            intidir = "/var/shootmaster/ERGEBNIS/XML"
        filename = askopenfilename(initialdir = initdir, parent = self.mainWindow.root, title = "Datei auswählen", filetypes = [("xml","*.xml")])
        if (filename):
            self.resultFile.set(filename)
            self.parseResultFile(filename)
            self.mainWindow.enableShowShooter()
            self.mainWindow.notebook.tab(2, state="normal")
            self.mainWindow.notebook.tab(3, state="normal")

    def parseResultFile(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        self.results = []
        self.shooterList = set()
        for child in root:
            shooter = {}
            shooter["targetID"] = child.attrib["TargetID"]
            shooter["gender"] = child.find("Shooter").find("Gender").text
            shooter["class"] = child.find("MatchClass").find("Name").text
            shooter["club"] = child.find("Club").find("Name").text
            shooter["lastname"] = child.find("Shooter").find("FamilyName").text
            shooter["firstname"] = child.find("Shooter").find("GivenName").text
            name = shooter["firstname"] + " " + shooter["lastname"] + ", " + shooter["club"]
            if (name not in self.shooterList):
                self.shooterList.add(name)
            shooter["shots"] = []
            for aiming in child.find("Aimings").find("AimingData").iter("Shot"):
                shot = {}
                shot["timestamp"] = aiming.find("TimeStamp").find("DateTime").text
                shot["resolution"] = aiming.find("Coordinate").find("CCoordinate").attrib["Resolution"]
                shot["x"] = aiming.find("Coordinate").find("CCoordinate").find("X").text
                shot["y"] = aiming.find("Coordinate").find("CCoordinate").find("Y").text
                shot["factor"] = self.getDistance(0,0,shot["x"],shot["y"])
                shooter["shots"].append(shot)
            self.results.append(shooter)
        self.shooterCount.set(str(len(self.results)) + " Scheiben von " + str(len(self.shooterList)) + " Schützen")

    def evaluateResult(self):
        scoring = self.config.scoring.get()
        # evaluate results
        for shooter in self.results:
            shots = 0
            for shot in shooter["shots"]:
                if (scoring == "min"):
                    shot["values"] = self.getFieldValue(self.getTouchedFields(shot))
                    shot["result"] = min(shot["values"])
                elif (scoring == "max"):
                    shot["values"] = self.getFieldValue(self.getTouchedFields(shot))
                    shot["result"] = max(shot["values"])
                elif (scoring == "cov"):
                    shot["values"] = self.getFieldValue(self.getCenterField(shot))
                    shot["result"] = shot["values"]
                elif (scoring == "sum"):
                    shot["values"] = self.getFieldValue(self.getTouchedFields(shot))
                    shot["result"] = sum(shot["values"])
                shots = shots + shot["result"]
            shooter["result"] = shots
        # sort results in descending order of result
        self.results.sort(key=lambda x: x["result"], reverse=True)
        # create html output of result
        self.html = "<html><head><meta charset='utf-8'></head><body><h1>Ergebnisse der Gl&uuml;cksscheibe</h1><h4>Datum: " + str(datetime.date.today()) + "</h4><table><tr><th>Name:</th><th>Punkte:</th></tr>"
        for shooter in self.results:
            self.html = self.html + "<tr><td>" + shooter["firstname"] + " " + shooter["lastname"] + "</td><td>" + str(shooter["result"]) + "</td></tr>"
        self.html = self.html + "</table></body></html>"

    def getTouchedFields(self, shot):
        hits = []
        center = self.getCenterField(shot)
        hits.append(center)
        horizontalOffset = int(shot["x"]) / int(shot["resolution"])
        verticalOffset = int(shot["y"]) / int(shot["resolution"])
        # look horizontal left
        y = center[1]
        x = center[0] - 1
        while (x >= 0) and ((horizontalOffset - (self.config.bulletSize.get() / 2)) < self.config.horizontal[x + 1]):
            hits.append([x,y])
            x = x - 1
        # look horizontal right
        x = center[0] + 1
        while (x < len(self.config.horizontal)) and ((horizontalOffset + (self.config.bulletSize.get() / 2)) > self.config.horizontal[x]):
            hits.append([x,y])
            x = x + 1
        # look vertical top
        x = center[0]
        y = center[1] - 1
        while (y >= 0) and ((verticalOffset + (self.config.bulletSize.get() / 2)) > self.config.vertical[y + 1]):
            hits.append([x,y])
            # look upper left
            x = center[0] - 1
            while (x >= 0) and (self.getDistance(horizontalOffset, verticalOffset, self.config.horizontal[x + 1], self.config.vertical[y + 1]) < (self.config.bulletSize.get() / 2)):
                hits.append([x,y])
                x = x - 1
            # look upper right
            x = center[0] + 1
            while (x < len(self.config.horizontal)) and (self.getDistance(horizontalOffset, verticalOffset, self.config.horizontal[x], self.config.vertical[y + 1]) < (self.config.bulletSize.get() / 2)):
                hits.append([x,y])
                x = x + 1
            y = y - 1
        # look vertical bottom
        x = center[0]
        y = center[1] + 1
        while (y < len(self.config.vertical)) and ((verticalOffset - (self.config.bulletSize.get() / 2)) < self.config.vertical[y]):
            hits.append([x,y])
            # look lower left
            x = center[0] - 1
            while (x >= 0) and (self.getDistance(horizontalOffset, verticalOffset, self.config.horizontal[x + 1], self.config.vertical[y]) < (self.config.bulletSize.get() / 2)):
                hits.append([x,y])
                x = x - 1
            # look lower right
            x = center[0] + 1
            while (x < len(self.config.horizontal)) and (self.getDistance(horizontalOffset, verticalOffset, self.config.horizontal[x], self.config.vertical[y]) < (self.config.bulletSize.get() / 2)):
                hits.append([x,y])
                x = x + 1
            y = y + 1
        return hits
    
    def getDistance(self, x1, y1, x2, y2):
        dx = int(x1) - int(x2)
        dy = int(y1) - int(y2)
        return math.sqrt(dx * dx + dy * dy)

    def getCenterField (self, shot):
        horizontalOffset = int(shot["x"]) / int(shot["resolution"])
        for x in range(len(self.config.horizontal)):
            if (self.config.horizontal[x] > horizontalOffset):
                x = x - 1
                break
        verticalOffset = int(shot["y"]) / int(shot["resolution"])
        for y in range(len(self.config.vertical)):
            if (self.config.vertical[y] < verticalOffset):
                y = y - 1
                break
        return [x,y]

    def getFieldValue(self, field):
        if isinstance(field[0], list):
            val = []
            for f in field:
                val.append(self.config.values[f[1]][f[0]])
            return val
        else:
            return self.config.values[field[1]][field[0]]

class MainWindow:

    def __init__(self, root):
        self.root = root
        self.frame = ttk.Frame(self.root)
        self.root.title("Glücksscheibengenerator")
        self.root.resizable(True, True)
        self.create_variables()
        self.create_widgets()
        self.grid_widgets()
        
    def create_variables(self):
        self.config = PaneConfig(self.root, self)
        self.results = Results(self.root, self)
        
    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.bind("<<NotebookTabChanged>>", self.notebookTabChangedEvent)
        self.back = ttk.Button(self.root, text='Zurück', command=self.back)
        self.next = ttk.Button(self.root, text='Weiter', command=self.next)

        # First Tab
        self.tabDefine = ttk.Frame(self.notebook)
        self.tabDefine.grid(column=0, row=0, sticky=(N, W, E, S))
        self.notebook.add(self.tabDefine, text = "Glücksscheibe definieren")
        self.tabDefine.grid_columnconfigure(0, weight=1)
        self.tabDefine.grid_columnconfigure(2, weight=1)
        self.tabDefine.grid_columnconfigure(4, weight=1)
        self.paneWidthLabel = ttk.Label(self.tabDefine, text='Breite der Scheibe (cm):')
        self.paneWidthEntry = ttk.Entry(self.tabDefine, width=4, textvariable=self.config.paneWidth)
        self.paneHeightLabel = ttk.Label(self.tabDefine, text='Höhe der Scheibe (cm):')
        self.paneHeightEntry = ttk.Entry(self.tabDefine, width=4, textvariable=self.config.paneHeight)
        self.bulletSizeLabel = ttk.Label(self.tabDefine, text='Kugeldurchmesser (mm)')
        self.bulletSizeEntry = ttk.Entry(self.tabDefine, width=4, textvariable=self.config.bulletSize)
        self.gridColumnsLabel = ttk.Label(self.tabDefine, text='Anzahl Spalten:')
        self.gridColumnsEntry = ttk.Entry(self.tabDefine, width=4, textvariable=self.config.gridColumns)
        self.gridRowsLabel = ttk.Label(self.tabDefine, text='Anzahl Zeilen:')
        self.gridRowsEntry = ttk.Entry(self.tabDefine, width=4, textvariable=self.config.gridRows)
        self.valuesMinLabel = ttk.Label(self.tabDefine, text='Kleinster Wert:')
        self.valuesMinEntry = ttk.Entry(self.tabDefine, width=4, textvariable=self.config.valuesMin)
        self.valuesMaxLabel = ttk.Label(self.tabDefine, text='Größter Wert:')
        self.valuesMaxEntry = ttk.Entry(self.tabDefine, width=4, textvariable=self.config.valuesMax)
        self.valuesStepsLabel = ttk.Label(self.tabDefine, text='Schrittgröße:')
        self.valuesStepsEntry = ttk.Entry(self.tabDefine, width=4, textvariable=self.config.valuesSteps)
        self.defineSeparator = ttk.Separator(self.tabDefine, orient='horizontal')
        self.loadPaneButton = ttk.Button(self.tabDefine, text='Glücksscheibe laden', command=self.loadPane)
        self.createPaneButton = ttk.Button(self.tabDefine, text='Glücksscheibe erzeugen', command=self.createPane)
        self.showPaneButton = ttk.Button(self.tabDefine, text='Glücksscheibe anzeigen', command=self.showPaneWindow, state=DISABLED)
        self.configFileLabel = ttk.Label(self.tabDefine, textvariable=self.config.configFile)

        # Second Tab
        self.tabLoad = ttk.Frame(self.notebook)
        self.tabLoad.grid(column=0, row=0, sticky=(N, W, E, S))
        self.notebook.add(self.tabLoad, text = "Ergebnisse laden", state=DISABLED)
        self.loadResultButton = ttk.Button(self.tabLoad, text='Datei laden', command=self.loadResult)
        self.resultFileLabel = ttk.Label(self.tabLoad, textvariable=self.results.resultFile)
        self.loadSeparator = ttk.Separator(self.tabLoad, orient='horizontal')
        self.showShooter = ttk.Button(self.tabLoad, text='Schützen anzeigen', command=self.showShooterWindow)
        self.shooterCountLabel = ttk.Label(self.tabLoad, textvariable=self.results.shooterCount)

        # Third Tab
        self.tabTeams = ttk.Frame(self.notebook)
        self.tabTeams.grid(column=0, row=0, sticky=(N, W, E, S))
        self.notebook.add(self.tabTeams, text = "Teams", state=DISABLED)
        self.showTeamDefinitionButton = ttk.Button(self.tabTeams, text='Teams festlegen' ,command=self.showTeamWindow, state=DISABLED)

        # Fourth Tab
        self.tabEvaluate = ttk.Frame(self.notebook)
        self.tabEvaluate.grid(column=0, row=0, sticky=(N, W, E, S))
        self.notebook.add(self.tabEvaluate, text = "Auswertung", state=DISABLED)
        self.scoringFrame = ttk.Labelframe(self.tabEvaluate, text='Falls Treffer mehrere Felder berührt, werte:')
        for text, mode in self.config.scoringOptions:
            b = ttk.Radiobutton(self.scoringFrame, text=text, variable=self.config.scoring, value=mode, command=self.results.evaluateResult)
            b.pack(side=LEFT, ipadx=10)
        self.teamScoringFrame = ttk.Labelframe(self.tabEvaluate, text='Falls Anzahl Schieben unterschiedlich, werte:')
        for text, mode in self.config.teamScoringOptions:
            b = ttk.Radiobutton(self.teamScoringFrame, text=text, variable=self.config.teamScoring, value=mode, command=self.results.evaluateResult)
            b.pack(side=LEFT, ipadx=10)
        self.separateGenderToggle = Checkbutton(self.tabEvaluate, text='Geschlechter getrennt auswerten', variable=self.config.separateGender, command=self.results.evaluateResult)
        self.separateAgeClassToggle = Checkbutton(self.tabEvaluate, text='Altersklassen getrennt auswerten', variable=self.config.separateAgeClass, command=self.results.evaluateResult)
        self.evaluateSeparator = ttk.Separator(self.tabEvaluate, orient='horizontal')
        self.showEvaluationButton = ttk.Button(self.tabEvaluate, text='Ergebnisse anzeigen', command=self.showEval)
        self.exportEvaluationPDFButton = ttk.Button(self.tabEvaluate, text='PDF exportieren', command=self.exportEvalPDF)
        self.exportEvaluationHTMLButton = ttk.Button(self.tabEvaluate, text='HTML exportieren', command=self.exportEvalHTML)

    def grid_widgets(self):
        innerOptions = dict(padx=5, pady=2)

        # First Tab
        self.paneWidthLabel.grid(column=0, row=0, sticky=E, **innerOptions)
        self.paneWidthEntry.grid(column=1, row=0, sticky=W, **innerOptions)
        self.paneHeightLabel.grid(column=2, row=0, sticky=E, **innerOptions)
        self.paneHeightEntry.grid(column=3, row=0, sticky=W, **innerOptions)
        self.bulletSizeLabel.grid(column=4, row=0, sticky=E, **innerOptions)
        self.bulletSizeEntry.grid(column=5, row=0, sticky=W, **innerOptions)
        self.gridColumnsLabel.grid(column=0, row=1, sticky=E, **innerOptions)
        self.gridColumnsEntry.grid(column=1, row=1, sticky=W, **innerOptions)
        self.gridRowsLabel.grid(column=2, row=1, sticky=E, **innerOptions)
        self.gridRowsEntry.grid(column=3, row=1, sticky=W, **innerOptions)
        self.valuesMinLabel.grid(column=0, row=2, sticky=E, **innerOptions)
        self.valuesMinEntry.grid(column=1, row=2, sticky=W, **innerOptions)
        self.valuesMaxLabel.grid(column=2, row=2, sticky=E, **innerOptions)
        self.valuesMaxEntry.grid(column=3, row=2, sticky=W, **innerOptions)
        self.valuesStepsLabel.grid(column=4, row=2, sticky=E, **innerOptions)
        self.valuesStepsEntry.grid(column=5, row=2, sticky=W, **innerOptions)
        self.defineSeparator.grid(column=0, columnspan=6, row=3, **innerOptions)
        self.loadPaneButton.grid(column=0, row=4, columnspan=2, **innerOptions)
        self.createPaneButton.grid(column=2, row=4, columnspan=2, **innerOptions)
        self.showPaneButton.grid(column=4, row=4, columnspan=2, **innerOptions)
        self.configFileLabel.grid(column=0, row=5, columnspan=6, **innerOptions)

        # Second Tab
        self.loadResultButton.grid(column=0, row=0, sticky=W, **innerOptions)
        self.resultFileLabel.grid(column=1, row=0, sticky=E, **innerOptions)
        self.loadSeparator.grid(column=0, columnspan=2, row=1, **innerOptions)
        self.showShooter.grid(column=0, row=2, stick=W, **innerOptions)
        self.shooterCountLabel.grid(column=1, row=2, sticky=E, **innerOptions)

        # Third Tab
        i = 0
        for text, mode in self.config.teamOptions:
            b = ttk.Radiobutton(self.tabTeams, text=text, variable=self.config.team, value=mode, command=self.teamSelectionChanged)
            b.grid(column=0, row=i, sticky=W, **innerOptions)
            i = i + 1
        self.showTeamDefinitionButton.grid(column=1, row=2, rowspan=2, sticky=NS, **innerOptions)

        # Fourth Tab
        self.scoringFrame.grid(column=0, row=0, columnspan=3, sticky=W, **innerOptions)
        self.teamScoringFrame.grid(column=0, row=1, columnspan=3, sticky=W, **innerOptions)
        self.evaluateSeparator.grid(column=0, columnspan=3, row=2, **innerOptions)
        self.separateGenderToggle.grid(column=0, columnspan=3, row=3, sticky=W, **innerOptions)
        self.separateAgeClassToggle.grid(column=0, columnspan=3, row=4, sticky=W, **innerOptions)
        self.showEvaluationButton.grid(column=0, row=5, **innerOptions)
        self.exportEvaluationPDFButton.grid(column=1, row=5, **innerOptions)
        self.exportEvaluationHTMLButton.grid(column=2, row=5, **innerOptions)

        # Pack all
        self.notebook.pack(fill="both", expand="yes")
        self.back.pack(side=LEFT, padx=20, pady=5)
        self.next.pack(side=RIGHT, padx=20, pady=5)
        self.disableShowShooter()

    def disableShowShooter(self):
        self.showShooter.state(["disabled"])

    def enableShowShooter(self):
        self.showShooter.state(["!disabled"])

    def notebookTabChangedEvent(self, event):
        self.currentTab = event.widget.index("current")
        self.next.state(["!disabled"])
        self.back.state(["!disabled"])
        if (self.config.currentTab == 0):
            self.back.state(["disabled"])
        if (self.config.currentTab == 3):
            self.evaluateResult()
            self.next.state(["disabled"])
        self.root.update()

    def next(self):
        self.notebook.select(self.config.currentTab + 1)

    def back(self):
        self.notebook.select(self.config.currentTab - 1)

    def loadPane(self):
        self.config.loadPane()
        self.showPaneButton.config(state="normal")
        self.notebook.tab(1 ,state="normal")

    def createPane(self):
        self.config.createPane()
        self.showPaneButton.config(state="normal")
        self.notebook.tab(1, state="normal")

    def savePane(self):
        self.config.savePane()

    def loadResult(self):
        self.results.loadResult()

    def showEval(self):
        self.showResultWindow()

    def exportEvalPDF(self):
        pdfkit.from_string(self.html, str(datetime.date.today()) + ".pdf")

    def exportEvalHTML(self):
        filename = os.getcwd() + "/" + str(datetime.date.today()) + ".html"
        f = open(filename, 'w')
        f.write(self.html)
        f.close()

    def teamSelectionChanged(self):
        if (self.config.team.get() == "person" or self.config.team.get() == "pane"):
            self.showTeamDefinitionButton.config(state="normal")
        else:
            self.showTeamDefinitionButton.config(state=DISABLED)

    def showShooterWindow(self):
        self.shooterWindow = Toplevel(self.root)
        ShooterWindow(self.shooterWindow, self.results, self.config)

    def showResultWindow(self):
        self.resultWindow = Toplevel(self.root)
        ResultWindow(self.resultWindow, self.result)

    def showPaneWindow(self, result=None, resultList=None):
        self.paneWindow = Toplevel(self.root)
        PaneWindow(self.paneWindow, result, resultList, self.config)

    def showTeamWindow(self):
        self.teamWindow = Toplevel(self.root)
        TeamWindow(self.teamWindow)

class ResultWindow:

    def __init__(self, master, result):
        self.root = root
        self.result = result
        self.root.title('Ergebnisse')
        self.self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.resizable(True, True)
        innerOptions = dict(padx=5, pady=2)
        frame = ttk.Frame(self.root)
        frame.pack()
        frame.grid_columnconfigure(0, weight=1)
        row = 0

        for shooter in self.results:
            nameLabel = ttk.Label(frame, text=shooter["firstname"] + " " + shooter["lastname"])
            nameLabel.grid(column=0, row=row, sticky=W, **innerOptions)
            resultLabel = ttk.Label(frame, text=str(shooter["result"]))
            resultLabel.grid(column=1, row=row, sticky=E, **innerOptions)
            showResultPane = ttk.Button(frame, text="Ergebnis anzeigen", command=lambda shooter=shooter: self.showPaneWindow(shooter))
            showResultPane.grid(column=2, row=row, sticky=E, **innerOptions)
            row = row + 1
        
class PaneWindow:

    def __init__(self, root, result, resultList, config):
        self.root = root
        self.result = result
        self.resultList = resultList
        self.config = config
        if (self.result):
            self.root.title("Ergebnis von " + self.result["firstname"] + " " + self.result["lastname"])
        else:
            self.root.title("Glücksscheibe")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.resizable(False, False)
        resizeFactor = 4
        offset = 3
        width = self.config.paneWidth.get() * 10 * resizeFactor + offset
        height = self.config.paneHeight.get() * 10 * resizeFactor + offset
        self.canvas = Canvas(self.root, width=width, height=height)
        self.canvas.grid(column=0, row=0)

        if self.result == None:
            self.canvas.bind('<Double-Button-1>', lambda event: self.canvasDoubleClick(event))

        # draw result list to select pane
        if (self.resultList):
            listbox = Listbox(self.root)
            listbox.grid(column=1, row=0)
            listbox.bind("<<ListboxSelect>>", lambda event: self.paneSelectionChanged(event))
            i = 0
            for resultItem in self.resultList:
                listbox.insert(int(i), self.resultList[i]["targetID"])
                if (self.result == self.resultList[i]):
                    listbox.selection_set(i)
                i = i + 1

        self.drawPaneGrid()

    def drawPaneGrid(self):
        self.canvas.delete("all")
        resizeFactor = 4
        offset = 3
        width = self.config.paneWidth.get() * 10 * resizeFactor + offset
        height = self.config.paneHeight.get() * 10 * resizeFactor + offset
        cellWidth = self.config.horizontalStep * resizeFactor
        cellHeight = self.config.verticalStep * resizeFactor
        bulletRadius = self.config.bulletSize.get() / 2 * resizeFactor
        horizontalOffset = abs(self.config.horizontal[0])
        verticalOffset = abs(self.config.vertical[0])

        # draw results if passed
        if self.result:
            innerOptions = dict(padx=5, pady=2)
            if (self.resultList == None):
                frame = ttk.Frame(self.root)
                frame.grid(column=1, row=0)
                frame.grid_columnconfigure(0, weight=1)

            i = 1
            for shot in self.result["shots"]:
                if (self.resultList == None):
                    shotLabel = ttk.Label(frame, text=str(i) + ": ")
                    shotLabel.grid(column=0, row=i - 1, sticky=E, **innerOptions)
                    resultLabel = ttk.Label(frame, text=str(shot["values"]))
                    resultLabel.grid(column=1, row=i - 1, sticky=W, **innerOptions)
                x = (int(shot["x"]) / int(shot["resolution"]) + horizontalOffset) * resizeFactor + offset
                y = height - (int(shot["y"]) / int(shot["resolution"]) + verticalOffset) * resizeFactor
                self.canvas.create_oval(x - bulletRadius, y - bulletRadius, x + bulletRadius, y + bulletRadius, fill='gray25')
                self.canvas.create_text(x, y, text=str(i), fill='white')
                i = i + 1

        # draw grid and values
        for line in self.config.horizontal:
            self.canvas.create_line((line + horizontalOffset) * resizeFactor + offset, 0, (line + horizontalOffset) * resizeFactor + offset, height)
        for line in self.config.vertical:
            self.canvas.create_line(0, (line + verticalOffset) * resizeFactor + offset, width, (line + verticalOffset) * resizeFactor + offset)
        for row in range(len(self.config.values)):
            for column in range(len(self.config.values[row])):
                x = (self.config.horizontal[column] + horizontalOffset) * resizeFactor + offset + cellWidth / 2
                y = (verticalOffset - self.config.vertical[row]) * resizeFactor + offset + cellHeight / 2
                self.canvas.create_text(x, y, text=str(self.config.values[row][column]))

    def paneSelectionChanged(self, event):
        self.result = self.resultList[event.widget.curselection()[0]]
        self.drawPaneGrid()
    
    def canvasDoubleClick(self, event):
        row = int(int(event.y) / (int(event.widget['height']) / int(self.config.gridRows.get())))
        col = int(int(event.x) / (int(event.widget['width']) / int(self.config.gridColumns.get())))
        self.showInputWindow(row, col)

    def showInputWindow(self, row, col):
        self.inputWindow = Toplevel(self.root)
        InputWindow(self.inputWindow, row, col, self, self.config)

class InputWindow:

    def __init__(self, root, row, col, parent, config):
        self.root = root
        self.parent = parent
        self.config = config
        self.row = row
        self.col = col
        self.root.title('Feld [' + str(self.row) + ", " + str(self.col) + "] anpassen")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.resizable(False, False)
        inputValue = IntVar(self.root, self.config.values[self.row][self.col])
        inputField = Entry(self.root, textvariable=inputValue)
        inputField.grid(column=0, row=0, columnspan=2, sticky=EW)
        inputField.focus_set()
        inputField.select_range(0, 'end')
        inputField.icursor('end')
        inputField.bind("<Return>", lambda event: self.changeValue(inputValue))
        cancelButton = ttk.Button(self.root, text='Abbrechen', command= lambda: self.closeInputWindow(self.root))
        cancelButton.grid(column=0, row=1)
        okButton = ttk.Button(root, text='Übernehmen', command= lambda: self.changeValue(inputValue))
        okButton.grid(column=1, row=1)
    
    def closeInputWindow(self):
        self.root.destroy()

    def changeValue(self, value):
        try:
            val = value.get()
            self.config.values[self.row][self.col] = val
            self.config.savePane()
            self.parent.drawPaneGrid()
            self.closeInputWindow()
        except:
            print("not a number")

class ShooterWindow:

    def __init__(self, root, results, config):
        self.root = root
        self.results = results
        self.config = config
        self.root.title('Schützen')
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.resizable(True, True)
        innerOptions = dict(padx=5, pady=2)
        frame = ttk.Frame(self.root)
        frame.pack()
        frame.grid_columnconfigure(0, weight=1)
        row = 0

        for shooter in self.results.shooterList:
            resultList = []
            for result in self.results.results:
                if (result["firstname"] + " " + result["lastname"] + ", " + result["club"] == shooter):
                    resultList.append(result)
            nameLabel = ttk.Label(frame, text=shooter)
            nameLabel.grid(column=0, row=row, sticky=W, **innerOptions)
            paneCount = ttk.Label(frame, text=str(len(resultList)) + " Scheiben")
            paneCount.grid(column=1, row=row, sticky=E, **innerOptions)
            showResultPane = ttk.Button(frame, text="Ergebnisse anzeigen", command=lambda resultList=resultList: self.showPaneWindow(resultList[0], resultList))
            showResultPane.grid(column=2, row=row, sticky=E, **innerOptions)
            row = row + 1

    def showPaneWindow(self, result=None, resultList=None):
        self.paneWindow = Toplevel(self.root)
        PaneWindow(self.paneWindow, result, resultList, self.config)

class TeamWindow:

    def __init__(self, root):
        self.root = root
        self.root.title("Teams definieren")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.resizable(False, False)
        innerOptions = dict(padx=5, pady=2)

        cancelButton = ttk.Button(self.root, text='Abbrechen')
        cancelButton.grid(column=0, row=0, sticky=W, **innerOptions)
        okButton = ttk.Button(self.root, text='Übernehmen')
        okButton.grid(column=1, row=0, sticky=W, **innerOptions)



def main(): 
    root = Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == '__main__':
    main()