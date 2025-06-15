# -*- coding: utf-8 -*-
# (für Umlaute)

########################################################################################################
# Dieses Skript, soll die Werte der HOD-Intensitäten einer .mdf-Datei in eine .txt-Datei speichern.
# Es sollen nur dann HOD-Intensitäten aufgezeichnet werden, wenn die Signale für die Relays 0 sind.
# Werte, die aufgezeichnet werden, sich aber außerhalb der Grenzen befinden, werden als Fehler vermerkt
# und in eine seperate Datei mit Fehlerwerten gepeichert. 
########################################################################################################

from asammdf import MDF, Signal # https://app.readthedocs.org/projects/asammdf/downloads/pdf/master/ Modul zum Arbeiten mit MDF-Dateien

import mdfreader # https://pypi.org/project/mdfreader/ Modul zum Arbeiten mit MDF-Dateien 

import glob # Modul zum Arbeiten mit Pfaden 

import pandas as pd # Modul Pandas, zum tabelarischen Verwalten von Datenmengen

import numpy as np # Module numpy zum erstellen von Arrays

import re # Regular Expression um in Strings nach Zeichenfolgen zu Suchen

# Variablen mit den Grenzwerten, die bei der Auswertung der HOD-Intensitäten zur Fehlererkennung dienen.
# Wenn Werte außerhalb der Grenzen erkannt werden, so sollen diese als Fehler mit Zeitstempel und 
# Signalnamen vermerkt werden.  
########################################################################################################
global UntereGrenze
UntereGrenze = 1.0 

global ObereGrenze 
ObereGrenze = 250.0
#######################################################################################################

# Wartezeit, nach sinkender Flanke der Relay-Signale, die keine Werte aufgenommen werden sollen
# nach Stand 5.2025 : 500ms, die Wartezeit wird in 20 ms Schritten berechnet
###################################################################################################### 
global WarteZeitin20msSchritten 
WarteZeitIn20msSchritten = 25   
######################################################################################################

# Muster der Hersteller Audi und JLR für die Erkennung der Signale, die Signalnamen der 
# Relays unterscheiden sich an dem letzten Zeichen \d+ für beliebige Dezimalzahl 
# Muster für die Signalnamen (regex, .* steht für beliebige Zeichen)
###############################################################################################################################
global signal_patterns

signal_patterns = [
        [r"Relay.*", r"Relay.*", r"Relay.*", r"HODExtIntensityZone2", r"HODExtIntensityZone3"],
        [r"Relay.*", r"Relay.*", r"Relay.*", r"KLR_Touchintensitaet_2", r"KLR_Touchintensitaet_3"],
       [r"HODExtIntensityZone2", r"HODExtIntensityZone3"],
       [r"KLR_Touchintensitaet_2", r"KLR_Touchintensitaet_3"]
    ]
###############################################################################################################################



def checkingForValidMdfFile():
    """
    In dieser Funktion soll geprüft werden ob eine .mdf-Datei im Ordner ist und ob diese die Signale für die Relais und
    Intensitäten ('HODExtIntensityZone2', 'HODExtIntensityZone3' oder 'KLR_Touchintensitaet_2', 'KLR_Touchintensitaet_3') enthält
    """
    # Prüfen ob eine .mdf-Datei im Ordner ist
    mdf_files = glob.glob('*.mdf*')
    # gibt eine Liste der .mdf-Dateien im Ordner an
    # und für Dateien mit Endung .mdf.mdf

    if not mdf_files:
        # leere Liste = keine Dateien
        print("Keine .mdf-Dateien gefunden.")
        return
    
    MdfFileCounter = 0
    # Variable für das Zählen der mdf-Dateien im Ordner für die Auswertung 

    global FlagIfMdfContainsValidSignals
    FlagIfMdfContainsValidSignals = 0
    # Variabel zum Verwalten, ob die aktuelle Datei die gesuchten Signale (Relays, HOD-Intensitäten) enthält

    while MdfFileCounter < len(mdf_files):
           # Läuft die Schleife für jede .mdf-Datei im Ordner durch 

             FlagIfMdfContainsValidSignals = Checking_If_Needed_Signals_In_Mdf(MdfFileCounter, *mdf_files)
             # Gibt 0 zurück, wenn Signale enthalten, sonst 1
        
             if FlagIfMdfContainsValidSignals == 0:
                  ReadingValuesWhenRelaysNotActive(MdfFileCounter, *mdf_files)
                  # Auswertung für HOD-Tests mit Relays 
                 
             if FlagIfMdfContainsValidSignals == 1:
                  print(f"{mdf_files[MdfFileCounter]} enthält keine gültigen Signale, keine Auswertung")
                    
             MdfFileCounter += 1
             FlagIfMdfContainsValidSignals = 0
             # Schleife wird itteriert und Flag für Untersuchung der Datei auf gültige Signale rückgesetzt 
    
       

def Checking_If_Needed_Signals_In_Mdf(MdfFileCounter, *mdf_files):
    """
    Prüft, ob die .mdf-Datei die benötigten Signale enthält (Audi oder JLR), auch wenn sich Kanalnummern ändern.
    Gibt 0 zurück, wenn gültig, sonst 1.
    """
    global Signale_Zum_Auswerten
    # Liste mit den Signalnamen, welche ausgewertet wrden sollen

    # Suche nach passenden Signalen mit regex
    info=mdfreader.MdfInfo()
    available_signals = info.list_channels(mdf_files[MdfFileCounter]) # returns only the list of channels

    for pattern_set in signal_patterns:  
       # Schleife über alle Signalgruppen (Audi/JLR), die jeweils alle benötigten Signale als Regex enthalten
       matched_signals = []             
       # Liste zum Speichern der tatsächlich gefundenen Signalnamen für dieses Pattern-Set
       for pattern in pattern_set:      
           # Schleife über jedes Signal-Regex-Muster im aktuellen Pattern-Set
           found = next((sig for sig in available_signals if re.fullmatch(pattern, sig)), None)
           # Suche das erste Signal in der Liste der verfügbaren Signale, das exakt auf das Regex-Muster passt
           if found:
               matched_signals.append(found) 
               # Wenn ein passendes Signal gefunden wurde, zur Liste hinzufügen
           else:
               break                         
           # Wenn ein Signal aus dem Set nicht gefunden wird, abbrechen und nächstes Pattern-Set prüfen
       if len(matched_signals) == len(pattern_set):  
           # Wenn alle Signale des Pattern-Sets gefunden wurden
           Signale_Zum_Auswerten = matched_signals   
           # Speichere die tatsächlich gefundenen Signalnamen global
           return 0                                 
       # Rückgabe 0: gültige Signale gefunden, Funktion kann beendet werden

    print(f"Datei {mdf_files[MdfFileCounter]} enthält keine gültigen Signale")
    return 1


def ReadingValuesWhenRelaysNotActive(MdfFileCounter, *mdf_files):

        """HOD-Intensitäten sollen eingelesen werden, wenn die Signale für die Relays NICHT geschaltet sind. Wenn die Relays an waren
        und ausgeschaltet worden sind, soll noch 500 ms gewartet werden bevor neue HOD-Intensitäten eingelesen werden können. 
        Wenn Werte eingelesen werden, die sich außerhalb der definierten Grenzen befinden, werden diese in eine seperate .txt-Datei
        (Fehlerwerte_NameMdfDatei.txt) geschrieben."""
        
        # Wenn die Mdf-Datei keine gültigen Signale enthält werden keine Werte notiert, Fuktion wird verlassen
        if FlagIfMdfContainsValidSignals != 0:
           return
        
        # Suche nach passenden Signalen mit regex
        info=mdfreader.MdfInfo()
        available_signals = info.list_channels(mdf_files[MdfFileCounter])
        # returns only the list of channels

        for pattern_set in signal_patterns:  
        # Schleife über alle Signalgruppen (Audi/JLR), die jeweils alle benötigten Signale als Regex enthalten
          matched_signals = []             
          # Liste zum Speichern der tatsächlich gefundenen Signalnamen für dieses Pattern-Set
          for pattern in pattern_set:      
           # Schleife über jedes Signal-Regex-Muster im aktuellen Pattern-Set
             found = next((sig for sig in available_signals if re.fullmatch(pattern, sig)), None)
           # Suche das erste Signal in der Liste der verfügbaren Signale, das exakt auf das Regex-Muster passt
             if found:
                matched_signals.append(found) 
               # Wenn ein passendes Signal gefunden wurde, zur Liste hinzufügen
             else:
                break                         
              # Wenn ein Signal aus dem Set nicht gefunden wird, abbrechen und nächstes Pattern-Set prüfen
             if len(matched_signals) == len(pattern_set):  
                  # Wenn alle Signale des Pattern-Sets gefunden wurden
                Signale_Zum_Auswerten = matched_signals   
                  # Speichere die tatsächlich gefundenen Signalnamen global
                return 0                                 
       # Rückgabe 0: gültige Signale gefunden, Funktion kann beendet werden
        
        if Signale_Zum_Auswerten == [r"Relay", r"Relay", r"Relay", r"HODExtIntensityZone2", r"HODExtIntensityZone3"] or Signale_Zum_Auswerten == [r"Relay", r"Relay", r"Relay", r"KLR_Touchintensitaet_2", r"KLR_Touchintensitaet_3"]:

            columns = Signale_Zum_Auswerten[3:]
        elif Signale_Zum_Auswerten == [ r"HODExtIntensityZone2", r"HODExtIntensityZone3"] or Signale_Zum_Auswerten == [r"KLR_Touchintensitaet_2", r"KLR_Touchintensitaet_3"] :
        
           Monitoring_2b_ReadingValues(MdfFileCounter, *mdf_files)
           # Es wird die Auswertung für Relay-loses 2B-Monitoring durchgeführt
           return
        
        else:
            print("Keine gültigen Signale gefunden, keine Auswertung")
            print(mdf_files[MdfFileCounter])
            return
            
        # Array zum Zählen der Spalten und Zeilen im DataFrame   
        ArrayForCounting = np.zeros((256,len(columns)), dtype=int)
        
        global df2
        df2 = pd.DataFrame(ArrayForCounting, columns = Signale_Zum_Auswerten[3:])
    
        global df
        yop = mdfreader.Mdf(mdf_files[MdfFileCounter])
        yop.resample(0.02)

        master_channel = list(yop.masterChannelList.keys())[0]
        df = yop.return_pandas_dataframe(master_channel)
        # Es wird die aktuell bearbeitete MDF-Datei in ein Panda-Tabelle umgewandelt 

        f = open(f"Datenübersicht_{mdf_files[MdfFileCounter].rstrip(".mdf")}.txt", "w")
        f.write(df.to_string())

        df2.index.name= "Intensitaetswerte"
        # Benennung des Indexes (Zeilennummerierung) des Dataframes, damit diese in das Textfile geschrieben werden kann
        
        MaßeArray = df.shape # gibt ein Array mit [Länge_DataFrame, Breite_DataFrame] zurück 
        LängeArray = MaßeArray[0] # erstes Element beschreibt die Länge

        c = open(f"Fehlerwerte_{mdf_files[MdfFileCounter].rstrip(".mdf")}.txt", "w")
        # Textdokument zum notieren der Fehlerwerte wird erstellt, mit dem Namen der jeweiligen 
        # .mdf-Datei ohne die Endung .mdf im Namen
        # https://www.w3schools.com/python/ref_string_rstrip.asp#:~:text=The%20rstrip()%20method%20removes,default%20trailing%20character%20to%20remove.

        c.write(f"Es werden nur Werte als Fehler anerkannt, die sich zwischen {UntereGrenze} und {ObereGrenze} befinden.")
        c.write("\n")

        for counter in range(3, len(Signale_Zum_Auswerten)):
          # Loop behandelt die ersten drei Signale in der Liste nicht (Relays-Signale)

            FlagRelay = 0
            # Flag zum prüfen der Flanken der Relay-Signale

            ItterationCounter = 0 
           
            while ItterationCounter < LängeArray:
            
                try: 
                    # Fehlerbehandlung, zum Überspringen, wenn keine Auszuwertenden Signale vorhanden sind 
                   
                        # Sind alle Relay-Signale Low?
                    if (df.iloc[ItterationCounter][ Signale_Zum_Auswerten[0]] or df.iloc[ItterationCounter] [Signale_Zum_Auswerten[1]] or df.iloc[ItterationCounter][Signale_Zum_Auswerten[2]]) == 0:

                        if FlagRelay == 0: 
                            # Relays wurden nicht vor kurzem ausgeschaltet (keine WarteZeit muss beachtet werden)
                            
                            y = float(df.iloc[ItterationCounter][Signale_Zum_Auswerten[counter]])
                            # Auslesen der Werte im DataFrame in der jeweiligen Spalte und 
                            # Zeile + Umwandlung in ein Float y ist ein Wert zwischen 0-255 

                            ArrayForCounting[(int(y),counter-3)] +=1
                            # Schreibt die Werte in ein Array an die jeweilige Zeile (y) und Spalte 1 oder 2,
                            # der Counter beginnt bei 3, weil die ersten 3 Signale in der Liste Relay-Signale 
                            # sind und nicht notiert werden

                            if y >= UntereGrenze and y <= ObereGrenze: 
                                # Wenn sich der eingelesene Wert außerhalb der Grenzen befindet,
                                # dann wird er in die für die Fehlerwerte mit dem Zeitstempel und dem Signalnamen notiert
          
                                c.write("\n")
                                c.write(f"{y} bei {df.iloc[ItterationCounter]['t']} s in Signal {Signale_Zum_Auswerten[counter]}")
                        if FlagRelay == 1:
                            # Wenn eine sinkende Flanke der Relay-Signale erkannt wurde, dann muss die Wartezeit eingehalten 
                            # werden, in dem die jeweiligen Stellen beim Auslesen des Dataframe übersprungen werden 
                            
                            ItterationCounter += WarteZeitIn20msSchritten
                            FlagRelay = 0
                            
                            continue
                
                    else:
                        FlagRelay = 1
                        # wenn die Relays an sind, wird das Flag gesetzt um die fallende Flanke der Relay-Signale zu erkennen

                    ItterationCounter += 1   
        
                except ValueError: 
                   
                    print("Value Error")
                    print("Keine Auszuwertenden Signale")
                    break  
                    
        c.close()
        WritingValuesToTextFile(MdfFileCounter, *mdf_files)


def ReadingValuesWhenRelaysNotActive_Working_Progress(MdfFileCounter, *mdf_files):

        """HOD-Intensitäten sollen eingelesen werden, wenn die Signale für die Relays NICHT geschaltet sind. Wenn die Relays an waren
        und ausgeschaltet worden sind, soll noch 500 ms gewartet werden bevor neue HOD-Intensitäten eingelesen werden können. 
        Wenn Werte eingelesen werden, die sich außerhalb der definierten Grenzen befinden, werden diese in eine seperate .txt-Datei
        (Fehlerwerte_NameMdfDatei.txt) geschrieben."""
        
        # Wenn die Mdf-Datei keine gültigen Signale enthält werden keine Werte notiert, Fuktion wird verlassen
        if FlagIfMdfContainsValidSignals != 0:
           return
        
        if Signale_Zum_Auswerten == [r"Relay", r"Relay", r"Relay", r"HODExtIntensityZone2", r"HODExtIntensityZone3"] or Signale_Zum_Auswerten == [r"Relay", r"Relay", r"Relay", r"KLR_Touchintensitaet_2", r"KLR_Touchintensitaet_3"]:

            columns = Signale_Zum_Auswerten[3:]
        elif Signale_Zum_Auswerten == [ r"HODExtIntensityZone2", r"HODExtIntensityZone3"] or Signale_Zum_Auswerten == [r"KLR_Touchintensitaet_2", r"KLR_Touchintensitaet_3"] :
        
           Monitoring_2b_ReadingValues(MdfFileCounter, *mdf_files)
           # Es wird die Auswertung für Relay-loses 2B-Monitoring durchgeführt
           return
        
        else:
            print("Keine gültigen Signale gefunden, keine Auswertung")
            print(mdf_files[MdfFileCounter])
            return
            
        # Array zum Zählen der Spalten und Zeilen im DataFrame   
        ArrayForCounting = np.zeros((256,len(columns)), dtype=int)
        
        global df2
        df2 = pd.DataFrame(ArrayForCounting, columns = Signale_Zum_Auswerten[3:])
    
        global df
        yop = mdfreader.Mdf(mdf_files[MdfFileCounter])
        yop.resample(0.02)

        master_channel = list(yop.masterChannelList.keys())[0]
        df = yop.return_pandas_dataframe(master_channel)
        # Es wird die aktuell bearbeitete MDF-Datei in ein Panda-Tabelle umgewandelt 

        f = open(f"Datenübersicht_{mdf_files[MdfFileCounter].rstrip(".mdf")}.txt", "w")
        f.write(df.to_string())

        df2.index.name= "Intensitaetswerte"
        # Benennung des Indexes (Zeilennummerierung) des Dataframes, damit diese in das Textfile geschrieben werden kann
        
        MaßeArray = df.shape # gibt ein Array mit [Länge_DataFrame, Breite_DataFrame] zurück 
        LängeArray = MaßeArray[0] # erstes Element beschreibt die Länge

        c = open(f"Fehlerwerte_{mdf_files[MdfFileCounter].rstrip(".mdf")}.txt", "w")
        # Textdokument zum notieren der Fehlerwerte wird erstellt, mit dem Namen der jeweiligen 
        # .mdf-Datei ohne die Endung .mdf im Namen
        # https://www.w3schools.com/python/ref_string_rstrip.asp#:~:text=The%20rstrip()%20method%20removes,default%20trailing%20character%20to%20remove.

        c.write(f"Es werden nur Werte als Fehler anerkannt, die sich zwischen {UntereGrenze} und {ObereGrenze} befinden.")
        c.write("\n")

        for counter in range(3, len(Signale_Zum_Auswerten)):
          # Loop behandelt die ersten drei Signale in der Liste nicht (Relays-Signale)

            FlagRelay = 0
            # Flag zum prüfen der Flanken der Relay-Signale

            ItterationCounter = 0 
           
            while ItterationCounter < LängeArray:
            
                try: 
                    # Fehlerbehandlung, zum Überspringen, wenn keine Auszuwertenden Signale vorhanden sind 
                   
                        # Sind alle Relay-Signale Low?
                    if (df.iloc[ItterationCounter][ Signale_Zum_Auswerten[0]] or df.iloc[ItterationCounter] [Signale_Zum_Auswerten[1]] or df.iloc[ItterationCounter][Signale_Zum_Auswerten[2]]) == 0:

                        if FlagRelay == 0: 
                            # Relays wurden nicht vor kurzem ausgeschaltet (keine WarteZeit muss beachtet werden)
                            
                            y = float(df.iloc[ItterationCounter][Signale_Zum_Auswerten[counter]])
                            # Auslesen der Werte im DataFrame in der jeweiligen Spalte und 
                            # Zeile + Umwandlung in ein Float y ist ein Wert zwischen 0-255 

                            ArrayForCounting[(int(y),counter-3)] +=1
                            # Schreibt die Werte in ein Array an die jeweilige Zeile (y) und Spalte 1 oder 2,
                            # der Counter beginnt bei 3, weil die ersten 3 Signale in der Liste Relay-Signale 
                            # sind und nicht notiert werden

                            if y >= UntereGrenze and y <= ObereGrenze: 
                                # Wenn sich der eingelesene Wert außerhalb der Grenzen befindet,
                                # dann wird er in die für die Fehlerwerte mit dem Zeitstempel und dem Signalnamen notiert
          
                                c.write("\n")
                                c.write(f"{y} bei {df.iloc[ItterationCounter]['t']} s in Signal {Signale_Zum_Auswerten[counter]}")
                        if FlagRelay == 1:
                            # Wenn eine sinkende Flanke der Relay-Signale erkannt wurde, dann muss die Wartezeit eingehalten 
                            # werden, in dem die jeweiligen Stellen beim Auslesen des Dataframe übersprungen werden 
                            
                            ItterationCounter += WarteZeitIn20msSchritten
                            FlagRelay = 0
                            
                            continue
                
                    else:
                        FlagRelay = 1
                        # wenn die Relays an sind, wird das Flag gesetzt um die fallende Flanke der Relay-Signale zu erkennen

                    ItterationCounter += 1   
        
                except ValueError: 
                   
                    print("Value Error")
                    print("Keine Auszuwertenden Signale")
                    break  
                    
        c.close()
        WritingValuesToTextFile(MdfFileCounter, *mdf_files)



def ReadingValuesWhenRelaysNotActive_Backup(MdfFileCounter, *mdf_files):

        """HOD-Intensitäten sollen eingelesen werden, wenn die Signale für die Relays NICHT geschaltet sind. Wenn die Relays an waren
        und ausgeschaltet worden sind, soll noch 500 ms gewartet werden bevor neue HOD-Intensitäten eingelesen werden können. 
        Wenn Werte eingelesen werden, die sich außerhalb der definierten Grenzen befinden, werden diese in eine seperate .txt-Datei
        (Fehlerwerte_NameMdfDatei.txt) geschrieben."""

        
        # Wenn die Mdf-Datei keine gültigen Signale enthält werden keine Werte notiert, Fuktion wird verlassen
        if FlagIfMdfContainsValidSignals != 0:
           return
        
        if len(Signale_Zum_Auswerten) > 3:
            # lieber: if Signale_Zum_Auswerte sind 
            #        [r"Relay.*", r"Relay.*", r"Relay.*", r"HODExtIntensityZone2", r"HODExtIntensityZone3"],
        #[r"Relay.*", r"Relay.*", r"Relay.*", r"KLR_Touchintensitaet_2", r"KLR_Touchintensitaet_3"],
            # 

            columns = Signale_Zum_Auswerten[3:]
        else:
           # else if Signale sind :  ,[ r"HODExtIntensityZone2", r"HODExtIntensityZone3"],
        # oder [, r"KLR_Touchintensitaet_2", r"KLR_Touchintensitaet_3"],
        # ausführen 
        ##
        # Else print("nix gefunden")
           Monitoring_2b_ReadingValues(MdfFileCounter, *mdf_files)
           # Es wird die Auswertung für Relay-loses 2B-Monitoring durchgeführt

           return
            
        # Array zum Zählen der Spalten und Zeilen im DataFrame   
        ArrayForCounting = np.zeros((256,len(columns)), dtype=int)
         
        global df2
        df2 = pd.DataFrame(ArrayForCounting, columns = Signale_Zum_Auswerten[3:])
    
        global df
        yop = mdfreader.Mdf(mdf_files[MdfFileCounter])
        yop.resample(0.02)

        master_channel = list(yop.masterChannelList.keys())[0]
        df = yop.return_pandas_dataframe(master_channel)
        # Es wird die aktuell bearbeitete MDF-Datei in ein Panda-Tabelle umgewandelt 

        f = open(f"Datenübersicht_{mdf_files[MdfFileCounter].rstrip(".mdf")}.txt", "w")
        f.write(df.to_string())

        df2.index.name= "Intensitaetswerte"
        # Benennung des Indexes (Zeilennummerierung) des Dataframes, damit diese in das Textfile geschrieben werden kann
        
        MaßeArray = df.shape # gibt ein Array mit [Länge_DataFrame, Breite_DataFrame] zurück 
        LängeArray = MaßeArray[0] # erstes Element beschreibt die Länge

        c = open(f"Fehlerwerte_{mdf_files[MdfFileCounter].rstrip(".mdf")}.txt", "w")
        # Textdokument zum notieren der Fehlerwerte wird erstellt, mit dem Namen der jeweiligen 
        # .mdf-Datei ohne die Endung .mdf im Namen
        # https://www.w3schools.com/python/ref_string_rstrip.asp#:~:text=The%20rstrip()%20method%20removes,default%20trailing%20character%20to%20remove.

        c.write(f"Es werden nur Werte als Fehler anerkannt, die sich zwischen {UntereGrenze} und {ObereGrenze} befinden.")
        c.write("\n")

        for counter in range(3, len(Signale_Zum_Auswerten)):
          # Loop behandelt die ersten drei Signale in der Liste nicht (Relays-Signale)

            FlagRelay = 0
            # Flag zum prüfen der Flanken der Relay-Signale

            ItterationCounter = 0 
           
            while ItterationCounter < LängeArray:
            
                try: 
                    # Fehlerbehandlung, zum Überspringen, wenn keine Auszuwertenden Signale vorhanden sind 
                   
                        # Sind alle Relay-Signale Low?
                    if (df.iloc[ItterationCounter][ Signale_Zum_Auswerten[0]] or df.iloc[ItterationCounter] [Signale_Zum_Auswerten[1]] or df.iloc[ItterationCounter][Signale_Zum_Auswerten[2]]) == 0:

                        if FlagRelay == 0: 
                            # Relays wurden nicht vor kurzem ausgeschaltet (keine WarteZeit muss beachtet werden)
                            
                            y = float(df.iloc[ItterationCounter][Signale_Zum_Auswerten[counter]])
                            # Auslesen der Werte im DataFrame in der jeweiligen Spalte und 
                            # Zeile + Umwandlung in ein Float y ist ein Wert zwischen 0-255 

                            ArrayForCounting[(int(y),counter-3)] +=1
                            # Schreibt die Werte in ein Array an die jeweilige Zeile (y) und Spalte 1 oder 2,
                            # der Counter beginnt bei 3, weil die ersten 3 Signale in der Liste Relay-Signale 
                            # sind und nicht notiert werden

                            if y >= UntereGrenze and y <= ObereGrenze: 
                                # Wenn sich der eingelesene Wert außerhalb der Grenzen befindet,
                                # dann wird er in die für die Fehlerwerte mit dem Zeitstempel und dem Signalnamen notiert
          
                                c.write("\n")
                                c.write(f"{y} bei {df.iloc[ItterationCounter]['t']} s in Signal {Signale_Zum_Auswerten[counter]}")
                        if FlagRelay == 1:
                            # Wenn eine sinkende Flanke der Relay-Signale erkannt wurde, dann muss die Wartezeit eingehalten 
                            # werden, in dem die jeweiligen Stellen beim Auslesen des Dataframe übersprungen werden 
                            
                            ItterationCounter += WarteZeitIn20msSchritten
                            FlagRelay = 0
                            
                            continue
                
                    else:
                        FlagRelay = 1
                        # wenn die Relays an sind, wird das Flag gesetzt um die fallende Flanke der Relay-Signale zu erkennen

                    ItterationCounter += 1   
        
                except ValueError: 
                   
                    print("Value Error")
                    print("Keine Auszuwertenden Signale")
                    break                
                    
        c.close()
        WritingValuesToTextFile(MdfFileCounter, *mdf_files)
        
        
def Monitoring_2b_ReadingValues(MdfFileCounter, *mdf_files):
    """HOD-Intensitäten sollen eingelesen werden, unabhängig von den Relay-Signalen, da bei dem 2B-Monitoring, keine Klemmen (Relays) anliegen und nur die HOD-Intensitäten
     über viele Stunden aufgezeichnet werden  ."""
        
    # Wenn die Mdf-Datei keine gültigen Signale enthält werden keine Werte notiert, Fuktion wird verlassen
    if FlagIfMdfContainsValidSignals != 0:
        return
        
    # Array zum Zählen der Spalten und Zeilen im DataFrame   
    ArrayForCounting = np.zeros((256,len(Signale_Zum_Auswerten)), dtype=int)
    
    global df2
    df2 = pd.DataFrame(ArrayForCounting, columns = Signale_Zum_Auswerten)
    # legt DataFrame für die auszulesenden Signale an 

    df2.index.name= "Intensitaetswerte"
    # Benennung des Indexes (Zeilennummerierung) des Dataframes, damit diese in das Textfile geschrieben werden kann
    
    global df
    yop = mdfreader.Mdf(mdf_files[MdfFileCounter])
    yop.resample(0.02)
    master_channel = list(yop.masterChannelList.keys())[0]
    df = yop.return_pandas_dataframe(master_channel)
    # Aktuelle mdf-Datei wird in panda umgewandelt
    yop.plot(Signale_Zum_Auswerten)

    f = open(f"Datenübersicht_{mdf_files[MdfFileCounter].rstrip(".mdf")}.txt", "w")
    f.write(df.to_string())

    MaßeArray = df.shape # gibt ein Array mit [Länge_DataFrame, Breite_DataFrame] zurück 
    LängeArray = MaßeArray[0] # erstes Element beschreibt die Länge


    c = open(f"Fehlerwerte_2b_{mdf_files[MdfFileCounter].rstrip(".mdf")}.txt", "w")
    # Textdokument zum notieren der Fehlerwerte wird erstellt, mit dem Namen der jeweiligen 
    # .mdf-Datei ohne die Endung .mdf im Namen
    # https://www.w3schools.com/python/ref_string_rstrip.asp#:~:text=The%20rstrip()%20method%20removes,default%20trailing%20character%20to%20remove.

    c.write(f"Es werden nur Werte als Fehler anerkannt, die sich zwischen {UntereGrenze} und {ObereGrenze} befinden.")
    c.write("\n")

    for counter in range(len(Signale_Zum_Auswerten)):
        ItterationCounter = 0 
        while ItterationCounter < (LängeArray):

                y = float(df.iloc[ItterationCounter, df.columns.get_loc(Signale_Zum_Auswerten[counter])])
                # Auslesen der Werte im DataFrame in der jeweiligen Spalte und 
                # Zeile + Umwandlung in ein Float y ist ein Wert zwischen 0-255 

                ArrayForCounting[(int(y),counter)] +=1,
                # Schreibt die Werte in ein Array an die jeweilige Zeile (y) und Spalte 1 oder 2,
                # der Counter beginnt bei 3, weil die ersten 3 Signale in der Liste Relay-Signale 
                # sind und nicht notiert werden

                if y >= UntereGrenze and y <= ObereGrenze: 
                # Wenn sich der eingelesene Wert außerhalb der Grenzen befindet,
                # dann wird er in die für die Fehlerwerte mit dem Zeitstempel und dem Signalnamen notiert
          
                    c.write("\n")
                    c.write(f"{y} bei {df.iloc[ItterationCounter]['t']} s in Signal {Signale_Zum_Auswerten[counter]}")  
                ItterationCounter += 1 
              
    c.close()
    Writing2b_ValuesToTxtFile(MdfFileCounter, *mdf_files)
   

def Writing2b_ValuesToTxtFile(MdfFileCounter, *mdf_files):
  
    f = open(f"Werte_2B_{mdf_files[MdfFileCounter].rstrip(".mdf")}.txt", "w")
    # Textdokument zum notieren der Werte wird erstellt, mit dem Namen der jeweiligen 
    # .mdf-Datei ohne die Endung .mdf im Namen
    # https://www.w3schools.com/python/ref_string_rstrip.asp#:~:text=The%20rstrip()%20method%20removes,default%20trailing%20character%20to%20remove.
    # https://www.w3schools.com/python/python_file_write.asp

    f.write(f"In dieser Datei werden die Intensitätswerte während des 2B-Monitorings aufgezeichnet")
    f.write("\n")
    f.write("\n")
    # Leerzeilen zur Übersicht

    f.write(df2.to_string())
    # Fügt ganzes DataFrame in Textdokument ein

    f.close()


def WritingValuesToTextFile(MdfFileCounter, *mdf_files):
        """Diese Funktion soll die erfassten Werte der HOD-Erkennung bei NICHT geschalteten Relays in 
        eine .txt-Datei (WertHäufung_NameMdfDatei.txt) schreiben"""   
        
        # Wenn die Mdf-Datei keine gültigen Signale enthält werden keine Werte notiert
        if FlagIfMdfContainsValidSignals != 0:
           return
                   
        f = open(f"WertHäufung_{mdf_files[MdfFileCounter].rstrip(".mdf")}.txt", "w")
        # Textdokument zum notieren der Werte wird erstellt, mit dem Namen der jeweiligen 
        # .mdf-Datei ohne die Endung .mdf im Namen
        # https://www.w3schools.com/python/ref_string_rstrip.asp#:~:text=The%20rstrip()%20method%20removes,default%20trailing%20character%20to%20remove.
        # https://www.w3schools.com/python/python_file_write.asp

        f.write(f"Wartezeit nach Aktivierung: {20* WarteZeitIn20msSchritten} ms wird in Variable 'WarteZeitIn20msSchritten' verwaltet")
        f.write("\n")
        f.write("\n")
        # Leerzeilen zur Übersicht

        f.write(df2.to_string())
        # Fügt ganzes DataFrame in Textdokument ein

        f.close()
        
        
if __name__ == "__main__":
    
    checkingForValidMdfFile()
    input("Drücken Sie eine 'Enter' um das Programm zu beenden ")

