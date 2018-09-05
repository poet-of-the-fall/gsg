#!/usr/local/bin/python3
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
# import tkinter for python2 or python3
try:
    # Python2
    from Tkinter import *
    import ttk as ttk
    from tkFileDialog import askopenfilename, asksaveasfile, asksaveasfilename
    from tkMessageBox import showwarning
except ImportError:
    # Python3
    from tkinter import *
    from tkinter import ttk
    from tkinter.filedialog import askopenfilename, asksaveasfile, asksaveasfilename
    from tkinter.messagebox import showwarning

class MainWindow(ttk.Frame):

    @classmethod
    def main(cls):
        NoDefaultRoot()
        root = Tk()
        root.title("Glücksscheibengenerator")
        app = cls(root)
        app.grid(sticky=NSEW)
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(0, weight=1)
        root.resizable(True, True)
        root.mainloop()

    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.create_variables()
        self.create_widgets()
        self.grid_widgets()

    def create_variables(self):
        self.paneWidth = DoubleVar(self, 17.0)
        self.paneHeight = DoubleVar(self, 17.0)
        self.bulletSize = DoubleVar(self, 4.5)
        self.gridColumns = IntVar(self, 17)
        self.gridRows = IntVar(self, 17)
        self.valuesMin = IntVar(self, 0)
        self.valuesMax = IntVar(self, 25)
        self.valuesSteps = IntVar(self, 5)
        self.ScoringOptions = [('Kleinsten Wert', 'min'), ('Größten Wert', 'max'), ('Meiste Abdeckung', 'cov'), ('Summe aller Werte', 'sum')]
        self.Scoring = StringVar(self, self.ScoringOptions[-1][1])
        self.file = StringVar(self, '')

    def create_widgets(self):
        self.generationFrame = ttk.Labelframe(self, text='Glücksscheibe definieren')
        self.generationFrame.grid_columnconfigure(0, weight=1)
        self.generationFrame.grid_columnconfigure(2, weight=1)
        self.generationFrame.grid_columnconfigure(4, weight=1)
        self.paneWidthLabel = ttk.Label(self.generationFrame, text='Breite der Scheibe (cm):')
        self.paneWidthEntry = ttk.Entry(self.generationFrame, width=4, textvariable=self.paneWidth)
        self.paneHeightLabel = ttk.Label(self.generationFrame, text='Höhe der Scheibe (cm):')
        self.paneHeightEntry = ttk.Entry(self.generationFrame, width=4, textvariable=self.paneHeight)
        self.bulletSizeLabel = ttk.Label(self.generationFrame, text='Kugeldurchmesser (mm)')
        self.bulletSizeEntry = ttk.Entry(self.generationFrame, width=4, textvariable=self.bulletSize)
        self.gridColumnsLabel = ttk.Label(self.generationFrame, text='Anzahl Spalten:')
        self.gridColumnsEntry = ttk.Entry(self.generationFrame, width=4, textvariable=self.gridColumns)
        self.gridRowsLabel = ttk.Label(self.generationFrame, text='Anzahl Zeilen:')
        self.gridRowsEntry = ttk.Entry(self.generationFrame, width=4, textvariable=self.gridRows)
        self.valuesMinLabel = ttk.Label(self.generationFrame, text='Kleinster Wert:')
        self.valuesMinEntry = ttk.Entry(self.generationFrame, width=4, textvariable=self.valuesMin)
        self.valuesMaxLabel = ttk.Label(self.generationFrame, text='Größter Wert:')
        self.valuesMaxEntry = ttk.Entry(self.generationFrame, width=4, textvariable=self.valuesMax)
        self.valuesStepsLabel = ttk.Label(self.generationFrame, text='Schrittgröße:')
        self.valuesStepsEntry = ttk.Entry(self.generationFrame, width=4, textvariable=self.valuesSteps)
        self.scoringLabel = ttk.Label(self.generationFrame, text='Falls Treffer mehrere Felder berührt, werte:')
        self.scoringFrame = ttk.Frame(self.generationFrame)
        for text, mode in self.ScoringOptions:
            b = ttk.Radiobutton(self.scoringFrame, text=text, variable=self.Scoring, value=mode)
            b.pack(side=LEFT, ipadx=10)
        self.loadPaneButton = ttk.Button(self.generationFrame, text='vorhandene Glücksscheibe laden', command=self.loadPane)
        self.createPaneButton = ttk.Button(self.generationFrame, text='Glücksscheibe erzeugen & speichern', command=self.createPane)
        self.showPaneButton = ttk.Button(self.generationFrame, text='Glücksscheibe anzeigen', command=self.showPane)

        self.evaluationFrame = ttk.Labelframe(self, text='Schießergebnisse Auswerten', width=1000)
        self.evaluationFrame.grid_columnconfigure(0, weight=1)
        self.evaluationFrame.grid_columnconfigure(1, weight=1)
        self.loadResultButton = ttk.Button(self.evaluationFrame, text='Datei laden & auswerten', command=self.loadResult)
        self.fileLabel = ttk.Label(self.evaluationFrame, textvariable=self.file)
        self.showEvaluationButton = ttk.Button(self.evaluationFrame, text='Ergebnisse anzeigen', command=self.showEval)
        self.exportEvaluationPDFButton = ttk.Button(self.evaluationFrame, text='PDF exportieren', command=self.exportEvalPDF)
        self.exportEvaluationHTMLButton = ttk.Button(self.evaluationFrame, text='HTML exportieren', command=self.exportEvalHTML)

        self.disableEvaluationButtons()
        self.disablePaneButtons()

    def grid_widgets(self):
        innerOptions = dict(padx=5, pady=2)
        self.generationFrame.pack(fill="both", expand="yes", padx=10, pady=10)
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
        self.scoringLabel.grid(column=0, row=3, columnspan=6, sticky=W, **innerOptions)
        self.scoringFrame.grid(column=0, row=4, columnspan=6, sticky=W, **innerOptions)
        self.loadPaneButton.grid(column=0, row=5, columnspan=2, sticky=W, **innerOptions)
        self.createPaneButton.grid(column=2, row=5, columnspan=2, sticky=W, **innerOptions)
        self.showPaneButton.grid(column=4, row=5, columnspan=2, sticky=W, **innerOptions)

        self.evaluationFrame.pack(fill="both", expand="yes", padx=10, pady=10)
        self.loadResultButton.grid(column=0, row=0, sticky=W, **innerOptions)
        self.fileLabel.grid(column=1, row=0, columnspan=2, sticky=E, **innerOptions)
        self.showEvaluationButton.grid(column=0, row=1, sticky=W, **innerOptions)
        self.exportEvaluationPDFButton.grid(column=1, row=1, sticky=W, **innerOptions)
        self.exportEvaluationHTMLButton.grid(column=2, row=1, sticky=W, **innerOptions)

    def loadPane(self):
        self.enablePaneButtons()
        config = configparser.ConfigParser()
        filename = askopenfilename(initialdir = os.getcwd(), parent = self.root, title = "Datei auswählen", filetypes = [("ini","*.ini")])
        config.read(filename)
        self.paneWidth.set(float(config['Settings']['paneWidth']))
        self.paneHeight.set(float(config['Settings']['paneHeight']))
        self.bulletSize.set(float(config['Settings']['bulletSize']))
        self.gridColumns.set(int(config['Settings']['gridColumns']))
        self.gridRows.set(int(config['Settings']['gridRows']))
        self.valuesMin.set(int(config['Settings']['valuesMin']))
        self.valuesMax.set(int(config['Settings']['valuesMax']))
        self.valuesSteps.set(int(config['Settings']['valuesSteps']))
        self.Scoring.set(config['Settings']['Scoring'])
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
        self.enablePaneButtons()
        filename = os.getcwd() + "/" + str(datetime.datetime.now()).replace(":", "-").replace(" ", "-") + ".ini"
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
        config.set('Settings', 'Scoring', self.Scoring.get())
        config.add_section('Pane')
        values = ''
        for element in self.values:
            values = values + ','.join(str(x) for x in element) + "/"
        values = values[:-1]
        config.set('Pane', 'values', values)
        config.write(cfgfile)
        cfgfile.close()

    def showPane(self):
        self.showPaneWindow()

    def loadResult(self):
        filename = askopenfilename(initialdir = os.getcwd(), parent = self.root, title = "Datei auswählen", filetypes = [("xml","*.xml")])
        self.file.set(filename)
        self.parseResultFile(filename)
        self.enableEvaluationButtons()

    def showEval(self):
        self.showResultWindow()

    def exportEvalPDF(self):
        pdfkit.from_string(self.html, str(datetime.date.today()) + ".pdf")

    def exportEvalHTML(self):
        filename = os.getcwd() + "/" + str(datetime.date.today()) + ".html"
        f = open(filename, 'w')
        f.write(self.html)
        f.close()

    def disablePaneButtons(self):
        self.showPaneButton.state(["disabled"])
    
    def enablePaneButtons(self):
        self.showPaneButton.state(["!disabled"])

    def disableEvaluationButtons(self):
        self.showEvaluationButton.state(["disabled"])
        self.exportEvaluationPDFButton.state(["disabled"])
        self.exportEvaluationHTMLButton.state(["disabled"])
    
    def enableEvaluationButtons(self):
        self.showEvaluationButton.state(["!disabled"])
        self.exportEvaluationPDFButton.state(["!disabled"])
        self.exportEvaluationHTMLButton.state(["!disabled"])

    def calculateGrid(self):
        self.horizontal = []
        self.horizontalStep = self.paneWidth.get() * 10 / self.gridColumns.get()
        for i in range(self.gridColumns.get() + 1):
            self.horizontal.append(i * self.horizontalStep - (self.paneWidth.get() * 10 / 2))
        self.vertical = []
        self.verticalStep = self.paneHeight.get() * 10 / self.gridRows.get()
        for i in range(self.gridRows.get() + 1):
            self.vertical.append((self.paneHeight.get() * 10 / 2) - i * self.verticalStep) 

    def parseResultFile(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        self.results = []
        id = 0
        for child in root:
            shooter = {}
            shooter["id"] = id
            shooter["lastname"] = child.find("Shooter").find("FamilyName").text
            shooter["firstname"] = child.find("Shooter").find("GivenName").text
            shooter["shots"] = []
            for aiming in child.find("Aimings").find("AimingData").iter("Shot"):
                shot = {}
                shot["resolution"] = aiming.find("Coordinate").find("CCoordinate").attrib["Resolution"]
                shot["x"] = aiming.find("Coordinate").find("CCoordinate").find("X").text
                shot["y"] = aiming.find("Coordinate").find("CCoordinate").find("Y").text
                shooter["shots"].append(shot)
            self.results.append(shooter)
            id = id + 1
        self.evaluateResult()

    def evaluateResult(self):
        scoring = self.Scoring.get()
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
        self.html = "<html><body><h1>Ergebnisse der Gl&uuml;cksscheibe</h1><h4>Datum: " + str(datetime.date.today()) + "</h4><table><tr><th>Name:</th><th>Punkte:</th></tr>"
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
        while (x >= 0) and ((horizontalOffset - (self.bulletSize.get() / 2)) < self.horizontal[x + 1]):
            hits.append([x,y])
            x = x - 1
        # look horizontal right
        x = center[0] + 1
        while (x < len(self.horizontal)) and ((horizontalOffset + (self.bulletSize.get() / 2)) > self.horizontal[x]):
            hits.append([x,y])
            x = x + 1
        # look vertical top
        x = center[0]
        y = center[1] - 1
        while (y >= 0) and ((verticalOffset + (self.bulletSize.get() / 2)) > self.vertical[y + 1]):
            hits.append([x,y])
            # look upper left
            x = center[0] - 1
            while (x >= 0) and (self.getDistance(horizontalOffset, verticalOffset, self.horizontal[x + 1], self.vertical[y + 1]) < (self.bulletSize.get() / 2)):
                hits.append([x,y])
                x = x - 1
            # look upper right
            x = center[0] + 1
            while (x < len(self.horizontal)) and (self.getDistance(horizontalOffset, verticalOffset, self.horizontal[x], self.vertical[y + 1]) < (self.bulletSize.get() / 2)):
                hits.append([x,y])
                x = x + 1
            y = y - 1
        # look vertical bottom
        x = center[0]
        y = center[1] + 1
        while (y < len(self.vertical)) and ((verticalOffset - (self.bulletSize.get() / 2)) < self.vertical[y]):
            hits.append([x,y])
            # look lower left
            x = center[0] - 1
            while (x >= 0) and (self.getDistance(horizontalOffset, verticalOffset, self.horizontal[x + 1], self.vertical[y]) < (self.bulletSize.get() / 2)):
                hits.append([x,y])
                x = x - 1
            # look lower right
            x = center[0] + 1
            while (x < len(self.horizontal)) and (self.getDistance(horizontalOffset, verticalOffset, self.horizontal[x], self.vertical[y]) < (self.bulletSize.get() / 2)):
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
        for x in range(len(self.horizontal)):
            if (self.horizontal[x] > horizontalOffset):
                x = x - 1
                break
        verticalOffset = int(shot["y"]) / int(shot["resolution"])
        for y in range(len(self.vertical)):
            if (self.vertical[y] < verticalOffset):
                y = y - 1
                break
        return [x,y]

    def getFieldValue(self, field):
        if isinstance(field[0], list):
            val = []
            for f in field:
                val.append(self.values[f[1]][f[0]])
            return val
        else:
            return self.values[field[1]][field[0]]

    def showResultWindow(self):
        root = Toplevel(self.root)
        root.title('Ergebnisse')
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(0, weight=1)
        root.resizable(True, True)
        innerOptions = dict(padx=5, pady=2)
        frame = ttk.Frame(root)
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
        
    def showPaneWindow(self, result=None):
        root = Toplevel(self.root)
        if (result):
            root.title("Ergebnis von " + result["firstname"] + " " + result["lastname"])
        else:
            root.title("Glücksscheibe")
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(0, weight=1)
        root.resizable(False, False)
        resizeFactor = 5
        offset = 3
        width = self.paneWidth.get() * 10 * resizeFactor + offset
        height = self.paneHeight.get() * 10 * resizeFactor + offset
        cellWidth = self.horizontalStep * resizeFactor
        cellHeight = self.verticalStep * resizeFactor
        bulletRadius = self.bulletSize.get() / 2 * resizeFactor
        horizontalOffset = abs(self.horizontal[0])
        verticalOffset = abs(self.vertical[0])
        canvas = Canvas(root, width=width, height=height)
        canvas.grid(column=0, row=0)

        # draw results if passed
        if result:
            frame = ttk.Frame(root)
            frame.grid(column=1, row=0)
            frame.grid_columnconfigure(0, weight=1)
            innerOptions = dict(padx=5, pady=2)

            i = 1
            for shot in result["shots"]:
                shotLabel = ttk.Label(frame, text=str(i) + ": ")
                shotLabel.grid(column=0, row=i - 1, sticky=E, **innerOptions)
                resultLabel = ttk.Label(frame, text=str(shot["values"]))
                resultLabel.grid(column=1, row=i - 1, sticky=W, **innerOptions)
                x = (int(shot["x"]) / int(shot["resolution"]) + horizontalOffset) * resizeFactor + offset
                y = height - (int(shot["y"]) / int(shot["resolution"]) + verticalOffset) * resizeFactor
                canvas.create_oval(x - bulletRadius, y - bulletRadius, x + bulletRadius, y + bulletRadius, fill='gray25')
                canvas.create_text(x, y, text=str(i), fill='white')
                i = i + 1

        # draw grid and values
        for line in self.horizontal:
            canvas.create_line((line + horizontalOffset) * resizeFactor + offset, 0, (line + horizontalOffset) * resizeFactor + offset, height)
        for line in self.vertical:
            canvas.create_line(0, (line + verticalOffset) * resizeFactor + offset, width, (line + verticalOffset) * resizeFactor + offset)
        for row in range(len(self.values)):
            for column in range(len(self.values[row])):
                x = (self.horizontal[column] + horizontalOffset) * resizeFactor + offset + cellWidth / 2
                y = (verticalOffset - self.vertical[row]) * resizeFactor + offset + cellHeight / 2
                canvas.create_text(x, y, text=str(self.values[row][column]))

if __name__ == '__main__':
    MainWindow.main()