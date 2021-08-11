import os
from datetime import datetime
from fvictorio import main


if __name__ == '__main__':

    root = os.getcwd()
    origin = os.path.join(root, 'data')
    output = os.path.join(root, 'output')
    filename = 'contacts.csv'

    if not os.path.exists(output):
        os.mkdir(output)
    
    main(origin, os.path.join(output, filename))