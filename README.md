# Glücksscheibengenerator (GSG)

Dieses Projekt wertet XML Exporte der Meyton Schießanlage als Glücksscheiben aus.

## Installation

Vorab bitte folgendes installieren:

- Python 3 (sollte vorinstalliert sein)
- PIP (sollte vorinstalliert sein)
- Tkinter (```sudo zypper install python3-tk```)
- [wkhtmltopdf](https://wkhtmltopdf.org) (falls installierbar)

und die benötigten Pakete mit PIP installieren

```bash
sudo pip install -r requirements.txt
```

Die erste Zeile in der **gsg.py** anpassen entsprechend dem Ergebnis von:

```bash
which python3
```

## Nutzung

Zuerst müssen die Ergebnisse exportiert werden. Dazu am besten eine eigene Scheibe in der Software von Meyton anlegen und eine Auswertung zu dieser Scheibe erstellen. Die Ergebnisse dieser Scheibe lassen sich dann als XLM exportieren. 

Hier ein paar Bilder zum Einrichten der Meyton Software:

1) Disziplin anlegen, dabei am besten "Trefferwert verdeckt, Treffer sichtbar" und "keine Probescheibe" wählen:
<img src="https://github.com/poet-of-the-fall/gsg/blob/master/pictures/1_Disziplin_erstellen.png?raw=true" width="446">

2) Dann oben auf das Icon zum definieren der Wertungscheibe klicken und ca so etwas einstellen:
<img src="https://github.com/poet-of-the-fall/gsg/blob/master/pictures/2_Scheibe_definieren.png?raw=true" width="446">

3) Eine Veranstlung bzw. Auswertung Anlegen und wie abgebildet einstellen:
<img src="https://github.com/poet-of-the-fall/gsg/blob/master/pictures/3_Auswertung_anlegen.png?raw=true" width="446">

4) Bei der Scheibenauswahl kann folgendes eingestellt werden (dann lässt sich die Glücksscheibe auch in anderen Veranstltungen verwenden):
<img src="https://github.com/poet-of-the-fall/gsg/blob/master/pictures/4_Scheiben_filtern.png?raw=true" width="446">

5) Wenn geschossen wurde, können die Ergebnise in der Auswertung als XML exportiert werden. Anschließend meldet das Programm, wohin die Daten gespeichert wurden (evtl. merken, da später die Daten von dort wieder geladen werden müssen):
<img src="https://github.com/poet-of-the-fall/gsg/blob/master/pictures/5_Ergebnisse_exportieren.png?raw=true" width="446">
<img src="https://github.com/poet-of-the-fall/gsg/blob/master/pictures/6_Pfad_merken.png?raw=true" width="446">

Jetzt kann das Glücksscheiben-Programm über das Terminal geöffnet werden, falls kein Shortcut am Desktop erstellt wurde:

```bash
./gsg.py
```

<img src="https://github.com/poet-of-the-fall/gsg/blob/master/pictures/mainwindow.png?raw=true" width="446">

Das exportierte Ergebnis kann jetzt im Glücksscheibengenerator verwendet werden. Hierzu folgernde Ablauf, der weiter unten noch ausführlicher beschrieben wird:

1) eine Glücksscheibe erzeugen oder laden
2) exportierte Ergebnisse laden
3) Auswertung anschauen/exportieren

**Glücksscheibe definieren**

Hier kann die Glücksscheibe beschrieben werden. Neben der Ausdehnung (Breite und Höhe) der Scheibe kann das Schachbrettmuster (Spalten und Zeilen) bestimmt werden. Für das automatische generieren von Zufallswerten für die Felder können Minimal- und Maximalwert sowie die Schrittgröße angegeben werden. Für die Wertung kann außerdem festgelegt werden, welcher Wert bei einem Treffer gewertet wird. Es steht zur Auswahl:

- Kleinster Wert: werden mehrere Felder abgedeckt, wird nur der Wert des Feldes mit der kleinsten Zahl gewertet
- Größter Wert: werden mehrere Felder abgedeckt, wird nur der Wert des Feldes mit der größten Zahl gewertet
- Meiste Abdeckung: werden mehrere Felder abgedeckt, wird nur des Feld mit der meisten Abdeckung gewertet (Mittelpunkt des Schusses)
- Summe aller Werte: Es werden alle Berührten Felder eines Schusses addiert

Durch einen Klick auf **Glücksscheibe erzeugen & speichern** wird aus den vorher angegeben Daten eine Glücksscheibe erstellt und automatisch im Ordner des Programms abgelegt.

Alte Glücksscheiben können jeder Zeit durch einen Klick auf **vorhandene Glücksscheibe laden** erneut geladen werden (hier die Datei der Glücksscheibe auswählen, die verwendet werden soll).

Mit **Glücksscheibe anzeigen** kann die aktuell geladene Glücksscheibe angezeigt werden. Es öffnet sich ein Fenster, dass dei Felder und deren Werte anzeigt.

**Schießergebnisse auswerten**

Zuerst muss die exportierte Datei mit den Ergebnissen geladen werden. Dazu auf **Datei laden & auswerten** klicken und die exportierte Datei angeben.

Mit einem Klick auf **Ergebnisse anzeigen** können die Ergebnisse der Schützen in einem neuen Fenster angezeigt werden. Das Ergebnis jedes Schützen lässt sich über **Ergebnis anzeigen** graphisch darstellen.

**Ergebnis exportieren** erzeugt eine PDF Datei im Ordner des Programms und kann für einen Ausdruck genutzt werden.

## Weitere Möglichkeiten

Falls gewünscht können die Werte der Glücksscheibe auch selbst definiert werden. Dazu einfach eine Scheibe erzeugen und die **.ini** Datei öffnen. Hier ist am Ende der Datei ein Bereich mit der Definition der Werte:

```
[Pane]
values = ...
```

Die Werte sind hier nach Zeilen und Spalten durch Kommata und Schrägstrich getrennt. Die Werte können geändert werden, müssen aber der angegebenen Anzahl an Zeilen und Spalten entsprechen. Die Datei kann nach dem speichern einfach über **vorhandene Glücksscheibe laden** neu geladen werden.