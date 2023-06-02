from audiolazy import str2midi


def select_scale(scale_selection=1):
    note_names = []

    # scale_selection = int(input('select scale: ( 1) 10~109 2) major 3) pentatonic 4) C lydian)'))
    # scale_selection = 1

    # TODO: change to dictionary
    # Option 1: using 100 consecutive notes
    if(scale_selection == 1):
        for i in range(21, 21+88):
            note_names.append(i)
        isNoteStr = False

    # 4 octaves of major scale
    elif(scale_selection == 2):
        note_names = ['C2','D2','E2','F2','G2','A2','B2',
                    'C3','D3','E3','F3','G3','A3','B3',
                    'C4','D4','E4','F4','G4','A4','B4',
                    'C5','D5','E5','F5','G5','A5','B5']
        isNoteStr = True

    #4 octaves of major pentatonic scale 
    elif(scale_selection == 3):
        note_names = ['C2','D2','E2','G2','A2',
                    'C3','D3','E3','G3','A3',
                    'C4','D4','E4','G4','A4',
                    'C5','D5','E5','G5','A5']
        isNoteStr = True

    #custom note set (a voicing of a Cmaj13#11 chord, notes from C lydian)
    elif(scale_selection == 4):
        note_names = ['C1','C2','G2',
                    'C3','E3','G3','A3','B3',
                    'D4','E4','G4','A4','B4',
                    'D5','E5','G5','A5','B5',
                    'D6','E6','F#6','G6','A6']
        isNoteStr = True

    else: 
        print("please select available scale")

    if(isNoteStr):
        note_midis = [str2midi(n) for n in note_names] #make a list of midi note numbers 
    else:
        note_midis = note_names

    return note_midis


def map_value(value, min_value, max_value, min_result, max_result):
    '''maps value (or array of values) from one range to another'''
    
    result = min_result + (value - min_value)/(max_value - min_value)*(max_result - min_result)
    return result