from room import Room
from threads import RoomThread
import sys

def main():
    json_file = sys.argv[1]
    rt = RoomThread(Room(json_file))
    rt.start()


if __name__ == '__main__':
    main()