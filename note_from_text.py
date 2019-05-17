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


Dictionary = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5,
              'g':6, 'h':7, 'i':8, 'j':9, 'k':10, 'l':11,
              'm':12, 'n':13, 'o':14, 'p':15, 'q':16, 'r':17,
              's':18, 't':19, 'u':20, 'v':21, 'w':22, 'x':23,
              'y':24, 'z':25}

# count message to change midi channel sometimes
n = 0

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

    print(note, life, channel, volume)
    fs.noteon(channel, note, volume)
    sleep(life)
    fs.noteoff(channel, note)


def thread_note(n, sortie):
    thread = threading.Thread(target=sortie_to_note, args=(n, sortie))
    thread.start()


def test():
    text = "abcdefghijklmnopqrstuvwxyz"
    n = 1
    for t in text:
        #sortie_to_note(n, t)
        thread_note(n, t)
        n += 1
        sleep(1)

        

if __name__ == '__main__':
    set_audio()
    test()
