#!/usr/bin/env python3
# -*- coding: utf8 -*-


import pretty_midi
import numpy
from time import sleep
import threading
import fluidsynth

"""
Utilise FluidR3_GM.sf2
Installation:
    numpy
    pretty_midi
    fluidsynth
    FluidR3_GM.sf2
"""


class PlayOneMidiChannel:
    
    def __init__(self, channel, fonts):
        """self.channel 1 to 16"""

        self.channel = channel
        self.fonts = fonts
        self.set_audio()
        self.thread_dict = {}
        for i in range(128):
            self.thread_dict[i] = 0
            
    def set_audio(self):
        """note from 0 to 127 but all values are not possible in all bank
        life 0 to ?
        channel 1 to 16
        volume 0 to 127
        """
        self.fs = fluidsynth.Synth()
        self.fs.start(driver='alsa')
        sfid = self.fs.sfload(self.fonts)

        # TODO ce truc est spécific à FluidR3_GM.sf2
        #      .program_select(channel,    sfid,   bank,   bank number)
        self.fs.program_select(  1  ,      sfid,   0,      0  ) # yamaha grand piano
        self.fs.program_select(  2  ,      sfid,   0,      40 ) # violin
        self.fs.program_select(  3  ,      sfid,   0,      37 ) # pop bass
        self.fs.program_select(  4  ,      sfid,   0,      56 ) # trompet
        self.fs.program_select(  5  ,      sfid,   0,      66 ) # tenor sax
        self.fs.program_select(  6  ,      sfid,   0,      114) # steel drums
        self.fs.program_select(  7  ,      sfid,   0,      118) # synth drum
        self.fs.program_select(  8  ,      sfid,   0,      119) # reverse cymbal
        self.fs.program_select(  9  ,      sfid,   0,      116) # taiko drum
        self.fs.program_select(  10  ,     sfid,   8,      38 ) # Synth Bass 3
        self.fs.program_select(  11  ,     sfid,   0,      70 ) # basson
        self.fs.program_select(  12  ,     sfid,   0,      46 ) # harp
        self.fs.program_select(  13  ,     sfid,   0,      13 ) # xylophone
        self.fs.program_select(  14  ,     sfid,   0,      24 ) # nylon string guitar
        self.fs.program_select(  15  ,     sfid,   0,      25 ) # steel string guitar
        self.fs.program_select(  16  ,     sfid,   0,      29 ) # overdrive guitar
            
    def play_note(self, note, volume):
        
        self.fs.noteon(self.channel, note, volume)
        
        while self.thread_dict[note]:
            sleep(0.0001)
        # Sinon fin de la note
        #print("Fin du thread de la note:", note)
        self.fs.noteoff(self.channel, note)
        
    def thread_note(self, note, volume):
        """Le thread se termine si note_off"""

        #print("Lancement du thread de la note:", note)
        self.thread_dict[note] = 1
        thread = threading.Thread(target=self.play_note, args=(note, volume))
        thread.start()

    def play_partition(self, partition, FPS):
        """partition = [[(82,100)], [(82,100), (45,88)], [(0,0)], ...
        un item tous les 1/FPS"""

        print("Excécution d'une partition")
        for event in partition:
            nombre_de_note = len(event)
            note_en_cours = []
            for midi in range(nombre_de_note):
                note = int(event[midi][0])
                note_en_cours.append(note)
                volume = int(event[midi][1])
                
                # Lancement de la note si pas en cours
                if self.thread_dict[note] == 0:
                    self.thread_note(note, volume)

            # Fin des notes autres que les notes en cours
            for k, v in self.thread_dict.items():
                if v == 1:
                    if k not in note_en_cours:
                        self.thread_dict[k] = 0

            sleep(1/FPS)
            
        print("The end !")
        self.the_end()

    def the_end(self):
        """Fin  de tous les threads"""
        
        for i in range(128):
            self.thread_dict[i] = 0


class AnalyseMidiFile:
    """Analyse le fichier midi,
    trouve le nombre et le nom des instruments.
    Retourne la liste des notes sur une time lapse de chaque instrument.
    """
    
    def __init__(self, midi_file, FPS):
        """Un seul fichier midi
        FPS de 10 à 1000, 50 ou 100 est bien
        Plus le FPS est élevé, plus le temps de calcul est long !
        """
        
        self.midi_file = midi_file
        self.FPS = FPS
        
    def get_partitions(self):
        """Fait les étapes pour tous les instruments"""
        
        parts, instruments = self.analyse()
        partitions = []
        for instrument in instruments:
            instrument_roll = self.get_instrument_roll(parts[instrument])
            partition = self.get_partition(instrument_roll, instrument)
            partitions.append(partition)
        return partitions
                
    def analyse(self):
        """ Instrument 0 Nom: Bass    
            Instrument 1 Nom: Drums   
            Instrument 2 Nom: Piano   
            Instrument 3 Nom: Piano
            Instrument 4 Nom: Guitar
        Pb 2 pianos !!
        """
        midi_pretty_format = pretty_midi.PrettyMIDI(self.midi_file)
        instruments = midi_pretty_format.instruments
        nbi = len(instruments)
        print("Nombre d'intruments:", nbi)

        # Dict des partitions des instruments
        partitions_dict = {}
        instruments_list = []
        for i in range(nbi):
            nom = instruments[i].name
            instruments_list.append(nom)
            print("Instrument", i, "Nom:", nom)
            # Chaque partition est un array
            partitions_dict[nom] = instruments[i]
            
        return partitions_dict, instruments_list 
        
    def get_instrument_roll(self, partition):
        """Retourne un np.array de (128, FPS*durée du morceau en secondes)"""

        # La méthode get_piano_roll marche pour tous les instruments
        instrument_roll = partition.get_piano_roll(self.FPS)

        # 64 secondes soit 640 dixième de secondes
        #print("Taille du array:", instrument_roll.shape)  # (128, 640)

        return instrument_roll

    def get_partition(self, instrument_roll, instrument):
        """Conversion du numpy array en liste de note tous les FPS"""

        # Copie des lignes du array dans une liste de ligne
        lignes = []
        for i in range(instrument_roll.shape[1]):
            ligne = instrument_roll[:,i]
            lignes.append(ligne)

        # Analyse des lignes pour ne garder que les non nuls
        partition = []
        for e in lignes:
            notes = []
            for n in range(instrument_roll.shape[0]):
                if numpy.any(e[n] != numpy.float64(0)):
                    notes.append((n, e[n]))
            partition.append(notes)
            
        print("Nombre de note dans la partition de", instrument, ":", len(partition))
        return partition


def play_partition(channel, partition):
    fonts = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
    pomc = PlayOneMidiChannel(channel, fonts)
    pomc.play_partition(partition, FPS)


def thread_play_partition(channel, partition):
    """Le thread se termine si note_off"""

    thread = threading.Thread(target=play_partition, args=(channel, partition))
    thread.start()


if __name__ == '__main__':

    song_mid = [
        './music/Piano-Piece-Nr-10.mid',
        './music/Test_Midi_Serge_V2.mid',
        "./music/straight no chaser.mid",
        "./music/Thelonius Monk Well, You Needn't.mid",
        "./music/Thelonius Monk Blue monk.mid",
        "./music/Bossa_Nova_USA.mid",
        "./music/Midnight-Blues.mid",
        "./music/Thelonius Monk criss-cross.mid",
        "./music/Dave Brubeck Pick Up Sticks.mid",
        "./music/Three's a Crowd - Dave Brubeck.mid"
        ]

    FPS = 100
    amf = AnalyseMidiFile(song_mid[9], FPS)
    partitions = amf.get_partitions()
    print("Nombre de partition", len(partitions))

    thread_play_partition(3, partitions[0])
    thread_play_partition(7, partitions[1])
    thread_play_partition(1, partitions[3])
    thread_play_partition(13, partitions[4])
