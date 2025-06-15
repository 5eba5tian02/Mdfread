# Mdfread
python_mdf_read


# MDF_Schwellwert – Funktionsübersicht

Dieses Python-Projekt dient zur Auswertung von MDF-Dateien, insbesondere zur Analyse von Relais- und Intensitätssignalen. Im Folgenden werden alle Hauptfunktionen des Projekts erläutert.

---

## checkingForValidMdfFile

Diese Funktion prüft, ob sich im aktuellen Ordner MDF-Dateien befinden und ob diese die benötigten Signale (Relais und Intensitäten) enthalten. Für jede gefundene Datei wird geprüft, ob die Signalnamen zu den erwarteten Mustern passen. Falls ja, werden die Daten exportiert und weiterverarbeitet.

---

## Checking_If_Needed_Signals_In_Mdf

Diese Funktion prüft, ob eine gegebene MDF-Datei alle benötigten Signale enthält. Dabei werden die Signalnamen mit regulären Ausdrücken (Regex) verglichen, um auch unterschiedliche Kanalnummern zu berücksichtigen. Wird ein vollständiges Set gefunden, werden die tatsächlichen Signalnamen gespeichert und die Funktion gibt 0 zurück, andernfalls 1.

---

## ReadingValuesWhenRelaysNotActive

Diese Funktion liest die HOD-Intensitätswerte aus, wenn die Relais-Signale nicht aktiv sind. Nach dem Ausschalten der Relais wird eine Wartezeit eingehalten, bevor neue Werte eingelesen werden. Werte außerhalb definierter Grenzen werden in eine separate Fehlerdatei geschrieben.

---

## WritingValuesToTextFile

Diese Funktion speichert die ausgelesenen und gefilterten Werte in eine Textdatei. Sie dient der Dokumentation und weiteren Auswertung der Messdaten.

---

## Globale Variablen und Signal-Pattern

Im Skript werden verschiedene globale Variablen verwendet, z.B. für Grenzwerte, Wartezeiten und die Muster der Signalnamen (`signal_patterns`). Diese Muster ermöglichen die flexible Erkennung der benötigten Signale in den MDF-Dateien.

---

## Hinweise

- Die Signalnamen in den MDF-Dateien können variieren. Das Skript nutzt Regex, um verschiedene Varianten zu erkennen.
- Für die Verarbeitung wird das Paket `mdfreader` verwendet.
- Fehlerhafte oder unvollständige Dateien werden übersprungen und im Terminal ausgegeben.

---



# MDF_Schwellwert – Funktionsübersicht

Dieses Python-Projekt dient zur Auswertung von MDF-Dateien, insbesondere zur Analyse von Relais- und Intensitätssignalen. Die aktuelle Version verwendet das Paket **asammdf** für das Einlesen und Verarbeiten der MDF-Dateien. Im Folgenden werden alle Hauptfunktionen des Projekts erläutert.

---

## checkingForValidMdfFile

Diese Funktion prüft, ob sich im aktuellen Ordner MDF-Dateien befinden und ob diese die benötigten Signale (Relais und Intensitäten) enthalten. Für jede gefundene Datei wird geprüft, ob die Signalnamen zu den erwarteten Mustern passen. Falls ja, werden die Daten mit **asammdf** eingelesen, aufbereitet und weiterverarbeitet.

---

## Checking_If_Needed_Signals_In_Mdf

Diese Funktion prüft, ob eine gegebene MDF-Datei alle benötigten Signale enthält. Dabei werden die Signalnamen mit regulären Ausdrücken (Regex) verglichen, um auch unterschiedliche Kanalnummern oder Varianten im Namen zu berücksichtigen. Wird ein vollständiges Set gefunden, werden die tatsächlichen Signalnamen gespeichert und die Funktion gibt 0 zurück, andernfalls 1.

---

## ReadingValuesWhenRelaysNotActive

Diese Funktion liest die HOD-Intensitätswerte aus, wenn die Relais-Signale nicht aktiv sind. Nach dem Ausschalten der Relais wird eine Wartezeit eingehalten, bevor neue Werte eingelesen werden. Werte außerhalb definierter Grenzen werden in eine separate Fehlerdatei geschrieben.

---

## WritingValuesToTextFile

Diese Funktion speichert die ausgelesenen und gefilterten Werte in eine Textdatei. Sie dient der Dokumentation und weiteren Auswertung der Messdaten.

---

## Globale Variablen und Signal-Pattern

Im Skript werden verschiedene globale Variablen verwendet, z.B. für Grenzwerte, Wartezeiten und die Muster der Signalnamen (`signal_patterns`). Diese Muster ermöglichen die flexible Erkennung der benötigten Signale in den MDF-Dateien, auch wenn sich Kanalnummern oder Signalnamen ändern.

---

## Hinweise

- Die Signalnamen in den MDF-Dateien können variieren. Das Skript nutzt Regex, um verschiedene Varianten zu erkennen.
- Für die Verarbeitung wird jetzt das Paket **asammdf** verwendet.
- Fehlerhafte oder unvollständige Dateien werden übersprungen und im Terminal ausgegeben.
- Die Signalnamen werden mit asammdf ausgelesen und können mit `mdf.channels_db.keys()` oder per Iteration über `mdf.iter_channels()` angezeigt werden.

---


# Für neue Version:
# HOD-Intensitäten Auswertung aus MDF-Dateien

Dieses Skript dient dazu, die Werte der HOD-Intensitäten aus .mdf-Dateien auszulesen und in .txt-Dateien zu speichern. Die Auswertung erfolgt abhängig vom Status der Relais-Signale.

## Funktionsweise

- **Nur HOD-Intensitäten aufzeichnen, wenn Relais-Signale 0 sind:**  
  Es werden nur dann HOD-Intensitäten aufgezeichnet, wenn die Signale für die Relays nicht geschaltet sind (d.h. Wert 0).
- **Fehlerwerte erkennen:**  
  Werte, die außerhalb definierter Grenzen liegen, werden als Fehler erkannt und in eine separate Datei geschrieben.
- **Wartezeit nach Relais-Abschaltung:**  
  Nach dem Ausschalten der Relais wird eine Wartezeit von 500 ms (in 20 ms Schritten) eingehalten, bevor neue Werte aufgenommen werden.
- **Signal-Erkennung per Regex:**  
  Die Signalnamen werden per regulärem Ausdruck erkannt, um verschiedene Hersteller-Varianten (Audi/JLR) zu unterstützen.

## Dateien

- **Werte_2B_...txt:**  
  Enthält die Intensitätswerte während des 2B-Monitorings (ohne Relais).
- **Fehlerwerte_...txt:**  
  Listet Werte außerhalb der erlaubten Grenzen mit Zeitstempel und Signalnamen.
- **WertHäufung_...txt:**  
  Enthält die Häufigkeit der erfassten Werte bei nicht geschalteten Relais.
- **Datenübersicht_...txt:**  
  Übersicht aller ausgelesenen Werte aus der jeweiligen MDF-Datei.

## Grenzwerte

- Untere Grenze: 1.0
- Obere Grenze: 250.0

## Ablauf

1. **Prüfen, ob .mdf-Dateien im Ordner vorhanden sind.**
2. **Für jede Datei:**
   - Prüfen, ob die benötigten Signale vorhanden sind (Relay & HOD-Intensitäten).
   - Falls ja, Werte auslesen und auswerten.
   - Fehlerhafte Werte werden separat protokolliert.
   - Ergebnisse werden in Textdateien gespeichert.

## Benötigte Pakete

- `asammdf`
- `mdfreader`
- `pandas`
- `numpy`
- `re`
- `glob`

## Start

Das Skript kann direkt ausgeführt werden:

```sh
python Trying.py
```

Nach Abschluss wartet das Programm auf einen Tastendruck zum Beenden.

---

**Hinweis:**  
Die Signalnamen und das Verhalten sind auf die spezifischen Anforderungen von Audi und JLR angepasst. Die Erkennung erfolgt flexibel über reguläre Ausdrücke.
