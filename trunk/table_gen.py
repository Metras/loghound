
# TODO: change module name to 'operations' and add the other generators 
# for operations logs. 

def generate_day_tables(events):
    """
    Given a series of special events, table_gen returns a list of two Table
    objects that, taken together, represent operating logs for the day. 
    
    It returns two table events because each table takes up an entire page.  
    
    Usage: 
    
    # Three events in this example: turn off transmitter at 3:05am, 
    # test EAS at 5:45, and check tower lights at 6:17pm. 
    # Use whatever capitalization the logs require. 
    >>> table_gen([
    ... (datetime(2009, 10, 28, 3, 5),  'TURN OFF TRANSMITTER'),
    ... (datetime(2009, 10, 28, 5, 45), 'TEST EAS LIGHTS AND TURN ON TRANSMITTER'),
    ... (datetime(2009, 10, 28, 18,17),  'CHECK TOWER LIGHTS: READING =')     
    ... ])            
    [<Table>, <Table>]     
    """
    
def main():
    print generate_day_tables()

if __name__ == '__main__':
    main()
