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

*TODO Beispiel und Bilder einfügen*

Jetzt kann das Programm über das Terminal geöffnet werden:

```bash
./gsg.py
```

<img src="https://github.com/poet-of-the-fall/gsg/blob/master/pictures/mainwindow.png?raw=true" width="446">

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