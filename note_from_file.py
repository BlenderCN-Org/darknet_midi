#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""
Il faut installer pyfluidsynth

    sudo pip3 install pyfluidsynth

et FluidR3_GM.sf2
    sudo apt install fluidsynth fluid-soundfont-gm
    
"""


from time import sleep
import threading
import fluidsynth
import mido

# Créer une class pour éviter de global
global fs


def set_audio():
    global fs
    fs = fluidsynth.Synth()
    fs.start(driver='alsa')
    sfid = fs.sfload("/usr/share/sounds/sf2/FluidR3_GM.sf2")

    # .program_select(channel,    sfid,   bank,   bank number)
    fs.program_select(  1  ,      sfid,   0,      0  ) # yamaha grand piano
    fs.program_select(  2  ,      sfid,   0,      40 ) # violin
    fs.program_select(  3  ,      sfid,   0,      37 ) # pop bass
    fs.program_select(  4  ,      sfid,   0,      56 ) # trompet
    fs.program_select(  5  ,      sfid,   0,      66 ) # tenor sax
    fs.program_select(  6  ,      sfid,   0,      114) # steel drums
    fs.program_select(  7  ,      sfid,   0,      118) # synth drum
    fs.program_select(  8  ,      sfid,   0,      119) # reverse cymbal
    fs.program_select(  9  ,      sfid,   0,      116) # taiko drum
    fs.program_select(  10  ,     sfid,   0,      73 ) # flute
    fs.program_select(  11  ,     sfid,   0,      70 ) # basson
    fs.program_select(  12  ,     sfid,   0,      46 ) # harp
    fs.program_select(  13  ,     sfid,   0,      13 ) # xylophone
    fs.program_select(  14  ,     sfid,   0,      24 ) # nylon string guitar
    fs.program_select(  15  ,     sfid,   0,      25 ) # steel string guitar
    fs.program_select(  16  ,     sfid,   0,      29 ) # overdrive guitar
        

def sortie_to_note(n, sortie):
    channel = 1
    life = 0.1
    volume = 100

    for j in sortie:
        if n%4 == 0:
            channel = 9
            life = 0.5
        elif n%3 == 0:
            channel = 13
            life = 0.1
        else:
            channel = 1
            life = 0.1
        if j.isdigit():
            volume = 30 + 10*int(j)
        if not j.isdigit():
            sleep(0.01)
            note = 50 + 3*Dictionary[j]
            playNote(note, life, channel, volume)


def playNote(note, life, channel, volume):
    '''note from 0 to 127 but all values are not possible in all bank
    life 0 to ?
    channel 1 to 16
    volume 0 to 127
    '''

    global fs

    fs.noteon(channel, note, volume)
    sleep(life)
    fin = fs.noteoff(channel, note)
    

def thread_note(n, sortie):
    thread = threading.Thread(target=sortie_to_note, args=(n, sortie))
    thread.start()


def get_note_in_midi_file(midi_file):
    mid = mido.MidiFile(midi_file)

    for i, track in enumerate(mid.tracks):
        print('Track {}: {}'.format(i, track.name))
        n = 0
        for msg in track:
            print(n)
            # les 2 premières lignes sont différentes, et la dernière
            if not isinstance(msg, mido.Message):
                print(msg)
            #else:
            if n > 8:
                print("Message:")
                print(  "msg.note", msg.note,
                        "msg.type", msg.type,
                        "msg.velocity", msg.velocity,
                        "msg.time", msg.time)
                note = msg.note
                typ = msg.type
                vel = msg.velocity
                t = msg.time
                volume = 100
                channel = 1
                life = t/1000
                print(  "note", note,
                        "life", life,
                        "channel",channel,
                        "volume", volume)
                playNote(note, life, channel, volume)
            n += 1

            
if __name__ == '__main__':
    set_audio()
    #midi_file = '/home/serge/Bureau/music/Test_Midi_Serge_V2.mid'
    midi_file = '/home/serge/Bureau/music/mozart-piano-sonata-k333-movement1.mid'
    get_note_in_midi_file(midi_file)


"""
<meta message time_signature numerator=4 denominator=4 clocks_per_click=24 notated_32nd_notes_per_beat=8 time=0>
<meta message key_signature key='C' time=0>
<meta message set_tempo tempo=508475 time=0>
<meta message marker text='Fish-Polka' time=0>
<meta message end_of_track time=0>
Track 1: Accordion High
<meta message midi_port port=0 time=0>
<meta message track_name name='Accordion High' time=0>
<meta message text text='Fish Polka' time=0>
"""
