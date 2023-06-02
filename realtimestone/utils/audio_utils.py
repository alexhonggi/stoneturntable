from audiolazy import str2midi


def select_scale(scale_selection="piano"):
    # TODO: change to dictionary
    # Option 1: using 100 consecutive notes
    if(scale_selection == "piano"):
        note_names = list(range(21, 21+88))
        isNoteStr = False
    # 4 octaves of major scale
    elif(scale_selection == 'CMajor'):
        note_names = ['C2','D2','E2','F2','G2','A2','B2',
                      'C3','D3','E3','F3','G3','A3','B3',
                      'C4','D4','E4','F4','G4','A4','B4',
                      'C5','D5','E5','F5','G5','A5','B5']
        isNoteStr = True
    #4 octaves of major pentatonic scale 
    elif(scale_selection == 'CPentatonic'):
        note_names = ['C2','D2','E2','G2','A2',
                      'C3','D3','E3','G3','A3',
                      'C4','D4','E4','G4','A4',
                      'C5','D5','E5','G5','A5']
        isNoteStr = True
    #custom note set (a voicing of a Cmaj13#11 chord, notes from C lydian)
    elif(scale_selection == 'CLydian'):
        note_names = ['C1','C2','G2',
                      'C3','E3','G3','A3','B3',
                      'D4','E4','G4','A4','B4',
                      'D5','E5','G5','A5','B5',
                      'D6','E6','F#6','G6','A6']
        isNoteStr = True
    else: 
        print("Please select available scale.")

    if(isNoteStr):
        note_midis = [str2midi(n) for n in note_names] #make a list of midi note numbers 
    else:
        note_midis = note_names

    return note_midis



class ValMapper:
    def __init__(self, mode: str, value: float, min_value: float, max_value: float, min_bound: int, max_bound: int):
        self.mode = mode
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        self.min_bound = min_bound
        self.max_bound = max_bound

    def norm(self):
        return (self.value - self.min_value) / (self.max_value - self.min_value)

    def mapper(self):
        norm_value = self.norm()
        
        if self.mode == 'linear':
            result = norm_value
        elif self.mode == 'log':
            result = np.log(norm_value)
        elif self.mode == 'exp':
            result = np.exp(norm_value)
        elif self.mode == 'sin':
            result = np.sin(norm_value)
        else:
            raise ValueError(f"Invalid mode {self.mode}")
        
        return self.min_bound + (self.max_bound - self.min_bound) * result

    def __call__(self):
        return self.mapper()