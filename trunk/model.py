class show:    
    '''
    a record class for radio shows as they appear in the programming logs.
    '''
    def __init__(self, name, start, duration, engineer, producer, announcer):
        '''
        parameters: 
        
        name - string - name of the radio show as appears in the program guide
        start - integer between 0 and 23: the hour the show starts 
        duration - integer: hours
        engineer - string
        producer/announcer - string. use commas to separate multiple people.
        '''
        self.name = name
        self.start = start 
        self.duration = duration
        self.engineer = engineer
        self.producer = producer
        self.announcer = announcer
        # note: using a datetime for self.start doesn't make sense to
        # me, because self.start represents a periodic starting time,
        # not a datetime point. 
        
class signon:
    '''
    represents a normal transmission signon event, as 
    found in the programming schedule.     
    '''
    def __init__(self, time):        
        '''
        time -- an integer between 0 and 23. this is
        the hour the signon is scheduled to start.
        '''
        self.time = time
        
class signoff:
    'represents a normal transmission signoff event.'
    def __init__(self, time):
        '''
        time -- an integer between 0 and 23. this is
        the hour the signoff is scheduled to start.
        '''
        self.time = time

###### sample shows

# baseline
show1 = show('Music for Human Beings', 
            19, 1, 
            'Dr. Jalis As-Sakran', 
            'Lester Woods', 
            'Peace Child Peter')

# no engineer, announcer or producer
show2 = show("Oregon Girl", 
            20, 2,
            '', 
            '', 
            '')

# long engineer name
show3 = show('Jazz Train', 
            22, 1,
            'Dr. Jalis "Doctor" As-Sakran Jr.', 
            'Lester Woods, Pat Greenleaf',
            'Peace Child Peter, Prof Levine')

# long producer and announcer name
show4 = show("Terrashow", 
            23, 2,
            'Peace Child Peter',
            'Adam Bockelie, Ka Man Chan, Tracey Hayse, Elizabeth Jones, Yusung Lim, Emily Moberg', 
            'Tracey Hayse, Adam Bockelie, Elizabeth Jones, Ka Man Chan, Yusung Lim, Emily Moberg')
    
# long show name
show5 = show("Generoso's Bovine Ska and Polka and Rocksteady Show", 
            1, 2,
            'Gene', 
            'Gene', 
            'Gene')

# long show, engineer, producer and announcer name
show6 = show("DJ Awesome and The Wonder Friends and The Jazz Volcano", 
            5, 1,
            'Ali "Sweet Victory" Mohammad ', 
            'Adam Bockelie, Ka Man Chan, Tracey Hayse, Elizabeth Jones, Yusung Lim, Emily Moberg', 
            'Ka Man Chan, Adam Bockelie, Tracey Hayse, Emily Moberg, Elizabeth Jones, Yusung Lim')
    

signoff1 = signoff(6)
signon1 = signon(7)
signoff2 = signoff(3)
signon2 = signon(5)

# a list of day events. sprinkle in signon and signoff events
day = [signoff1, signon1, show1, show2, show3, show4, show5, signoff2, signon2, show6]
