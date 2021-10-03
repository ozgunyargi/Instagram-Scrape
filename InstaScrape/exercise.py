
import sys
from .Config.config import *

if __name__ == '__main__':

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-n", "--name", help="Name that you want to display",
            type="str", dest="name", default="")
    parser.add_option("-c", "--count", help="Count value",
            type="int", dest="count", default=1)

    parameters, args = parser.parse_args(sys.argv[1:])

    for c in range(parameters.count):
        print(PATH_)
