from room import Room
from threads import RoomThread, ConnectionThread
import sys

def main():
    json_file = sys.argv[1]
    rt = RoomThread(Room(json_file))
    ct = ConnectionThread(rt)
    ct.start()


if __name__ == '__main__':
    main()