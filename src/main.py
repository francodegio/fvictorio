import os
from datetime import datetime
from fvictorio import main


if __name__ == '__main__':

    workdir = os.getcwd()
    output = os.path.split(workdir)[0]
    output = os.path.join(output, 'ouput')
    filename = 'contacts.csv'

    if not os.path.exists(output):
        os.mkdir(output)
    
    main('../data', os.path.join(output, filename))