#!/usr/bin/python
# -*- coding: utf-8 -*-

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details.

"""
    Automatisches erstellen von Pinwandlinks für das WeTab
    ver 0.4 (29.10.2010)
        + buttons zum löschen der Eingabezeilen hinzugefügt
        + Benutzerabfrage hinzugefügt ob Pinnwand neu gestartet werden soll
    
    ver 0.5 (01.11.2010)
        + Dateipfad zur glade-Datei angepasst - unabhänging vom Ort des aufrufenden
          skripts. -> Programm startet jetzt auch von der Pinnwand aus
        + kleinen Hilfetext hinzugefügt
        
    ver 0.6 (04.11.2010)
        + neustarten der Pinnwand durch 'killall tiitoo-pinnwand'
        + testen des Programmaufrufs per GUI möglich
        + Widget hinzugefügt
    
    ver 0.7 (17.11.2010)
        + neues Icon mit ausliefern
        + Name der Icondatei wird an den Namen der *.desktop Datei angepasst
        + Hilfetext erweitert
        + testen ob Befehl im %PATH% existiert durch Programm/ Benutzerabfrage entfällt
    TODO:
        + Fehler beim kopieren abfangen und an Benutzer durchgeben
        + Dokumentation der Funktionen/Methoden aufräumen

"""

__version__ = '0.7'

import gtk
import os
import shutil
import subprocess

DEBUG = True

HOMEFOLDER = os.path.expanduser('~')
PINFOLDER = os.path.join(HOMEFOLDER,
                         '.appdata/tiitoo-pinnwand/tiitoo-localbookmarks/')
APPDIR = os.path.dirname(os.path.abspath(__file__))
GUI_FILE = os.path.join(APPDIR,'GUI.glade')

def get_file(folder, filter, text):
    """
        Mit Hilfe des FilechooserDialogs eine Datei im Verzeichnissystem auswählen
        @param folder: string - pfad zum Ordner von dem aus die suche gestartet werden soll
    """
    dlg = gtk.FileChooserDialog(title=text,
                                action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                         gtk.STOCK_OK, gtk.RESPONSE_OK))
    dlg.set_current_folder(folder)
    dlg.add_filter(filter)
    result = dlg.run()
    if result == gtk.RESPONSE_OK:
        file = dlg.get_filename()
    else:
        file = None
    dlg.destroy()
    return file


def dialog_fail_create(message):
    """
        Modalen Dialog für Fehlernachricht ausgeben
    """
    dlg = gtk.MessageDialog(type=gtk.MESSAGE_INFO,
                            buttons=gtk.BUTTONS_OK,
                            message_format='Fehler beim erstellen vom Pinnwandeintrag')
    dlg.format_secondary_text(message)
    result = dlg.run()
    dlg.destroy()

    
def dialog_restart_pinn():
    """
        Dialog zur Abfrage ob die Pinnwand neu gerstartet werden soll
    """
    dlg = gtk.MessageDialog(type=gtk.MESSAGE_QUESTION,
                            message_format='Pinnwand neu starten?',
                             buttons=gtk.BUTTONS_YES_NO)
    dlg.format_secondary_text('Icon wurde erstellt \n soll die Pinnwand jetzt neu gestartet werden?')
    result = dlg.run()
    if result == gtk.RESPONSE_YES:
       temp = True
    else:
       temp = False
    dlg.destroy()
    return temp

def check_in_path(script):
    """
        wenn Kein pfad zu einem Gültigen Script eingeben wurde besteht immer
        noch die Möglichkeit das ein Programm aus dem $PATH gestartet werden soll
    """
    print script
    try:
        executable, arg = script.split(' ')                
        # -> es wurde kein Argument mitgegeben        
    except ValueError:
                executable = script
    p = subprocess.Popen(['which', executable])
    p.communicate()
    if p.returncode == 0:
        return True
    return False
                
def display_message(title, message):
    """
        Nachricht in Modalem Dialog dem benutzer Anzeigen
    """
    dlg = gtk.MessageDialog(type=gtk.MESSAGE_INFO,
                            buttons=gtk.BUTTONS_OK,
                            message_format=title)
    dlg.format_secondary_text(message)
    dlg.run()
    dlg.destroy()

def check_valid(script, image, entry_name):
    """
        überprüfen ob die eingegeben Daten gültig sind
        TODO: Rückgabeparameter ändern (wenigstens keine Strings)
    """
    if entry_name == "":
        return False, 'kein gültiger Name für Eintrag angegeben'
    file_name = '.'.join([entry_name, 'desktop'])
    if os.path.exists(os.path.join(PINFOLDER, file_name)):
        return False, 'Pinnwandeintrag mit diesem Namen existiert bereits'
    if os.path.exists(image) == False:
        return False, 'kein Gültiger Pfad für zu verwendendes Bild angegeben'
    if os.path.basename(image).split('.')[1] != 'png':
        return False, 'keine png-Datei als Bild angegeben'
    if os.path.exists(script) == False:
        return False, 'kein Gültiger Pfad für zu startendes Script angegeben'
    return True, True
    
    
def create_entry(script, image, entry_name):
    """
        Eintrag auf der Pinnwand erstellen
        -> Bild Kopieren -> Dateiname an entry_name anpassen
        -> *.desktop Datei erstellen
    """
        #TODO: Fehler abfrangen und an Benutzer durchreichen
    shutil.copy(image, PINFOLDER)
    
    image_old = os.path.join(PINFOLDER, os.path.split(image)[1])
    image_new = os.path.join(PINFOLDER, entry_name+'.png')
    os.rename(image_old, image_new)
    
    file_name = '.'.join([entry_name, 'desktop'])
    with open(os.path.join(PINFOLDER, file_name), 'w') as f:
        f.write('[Desktop%20Entry]\n')
        f.write('Type=Application\n')
        f.write(''.join(['Icon=', os.path.basename(image_new), '\n']))
        f.write(''.join(['Exec="', script, '"\n']))
        f.close()


class MyGUI(object):
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file(GUI_FILE)
        self.builder.connect_signals(self)

        self.win = self.builder.get_object('window1')
        self.entry1 = self.builder.get_object('entry1')
        self.entry2 = self.builder.get_object('entry2')
        self.entry3 = self.builder.get_object('entry3')
        
        self.create_filters()
        
    def create_filters(self):
        """
            Filter für die Dateidialoge erstellen
        """
        self.png_filter = gtk.FileFilter()
        self.png_filter.add_pattern('*.png')
        
        self.script_filter = gtk.FileFilter()
        self.script_filter.add_pattern('*')
        
    def run(self):
        gtk.main()

    def quit(self):
        gtk.main_quit()
    
    def on_window1_delete_event(self, *args):
        self.quit()
       
    def on_button1_clicked (self, *args):
        """
            auszufürhendes script in Filesystem suchen und in entry1
            ablegen
        """
        file = get_file(HOMEFOLDER, self.script_filter, 'script suchen')
        if file != None:
            self.entry1.set_text(file)
        
    def on_button2_clicked(self, *args):
        """
            zu verwendende png- Datei in Filesystem suchen und in
            entry2 ablegen
        """
        file = get_file(HOMEFOLDER, self.png_filter, 'png-Datei suchen')
        if file != None:
            self.entry2.set_text(file)

    def on_button3_clicked(self, *args):
        """
            Programm beenden
        """
        self.quit()
    
    def on_button4_clicked(self, *args):
        """
            Überprüfen ob in entry1 und entry 2 Pfade zu gültigen Dateien
            stehen
            Überprüfen ob entry3 einen güligen Namen enthält unter dem noch
            kein Eintrag angelegt wurde
            danach kopieren der png-Datei und erstellen des 
            Pinnwandeintrags
        """ 
        result = check_valid(self.entry1.get_text(),
                             self.entry2.get_text(),
                             self.entry3.get_text())
        
        if result[0] == False:
            #bei ungültigem Pfad kann das Script immer noch im Path stehen und 
            #trotzdem funktionieren
                    #TODO: nicht über string lösen...
            if result[1] == 'kein Gültiger Pfad für zu startendes Script angegeben':
                if check_in_path(self.entry1.get_text()) == True:
                    result = True, True
                else:
                    dialog_fail_create(result[1])
                    
            else:
                dialog_fail_create(result[1])
                
        if result[0] == True:
            create_entry(self.entry1.get_text(),
                         self.entry2.get_text(),
                         self.entry3.get_text())
            
            if dialog_restart_pinn() == True:
                p = subprocess.Popen(['killall', 'tiitoo-pinnwand'])

    def on_button5_clicked(self, *args):
        """
            Inhalt von entry1 löschen - Zeile für zu startendes Programm
        """
        self.entry1.set_text('')
        
    def on_button6_clicked(self, *args):
        """
            Inhalt von entry2 löschen - Zeile für Icon
        """
        self.entry2.set_text('')
        
    def on_button7_clicked(self, *args):
        """
            Hilfe einblenden
        """        
        msg = ''.join(['Das zu startende Skript über "Datei suchen" eingeben oder per Hand',
                       ' eingeben. Grundsätzlich sind alle Befehle die in der Shell möglich',
                       ' sind gültig. Nicht benutzt werden dürfen Umlaute Leerzeichen und',
                       ' andere Sonderzeichen.\n\n',
                       'Die Icondatei muss im png-Format vorliegen und sollte in einer Größe',
                       ' von 168x105 pixeln vorliegen.\n\n',
                       'Der Name des Eintrages kann frei gewählt werden, muss einmalig sein'
                       ' und darf keine Umlaute, Sonderzeichen oder Leerzeichen enthalten.\n',
                       'Für Ausführlichere Hilfe bitte die Datei README lesen'
                       ])
        display_message('Hilfe zum Iconcreator', msg)
    
    def on_button8_clicked(self, *args):
        """
            Versuchen den Inhalt des Feldes für zu startendem Programm mit 
            subprocess auszuführen.
        """
        if self.entry1.get_text() != '':
                # wenn ein Argument mitgegeben wurde Aufruf und Argument trennen
            try:
                executable, arg = self.entry1.get_text().split(' ')
                arg_list = [executable, arg]
                                 
                # -> es wurde kein Argument mitgegeben        
            except ValueError:
                arg_list = [self.entry1.get_text()]

            try:
                p = subprocess.Popen(arg_list,
                                     stdout = subprocess.PIPE,
                                     stderr = subprocess.STDOUT)
                stdout, _ = p.communicate()
 
            except OSError, os_exception:
                    stdout = os_exception.strerror
                    
        else:
            stdout = 'keine Gültigen Eingabedaten'
            
        display_message('Rückgabewert nach Programmaufruf:', stdout)

if __name__ == '__main__':
    app = MyGUI()
    app.run()
    
    