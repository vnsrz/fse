from room import Room
from threads import RoomThread, ConnectionThread
import sys

def main():
    host = "127.0.0.1"
    port = 34315
    
    json_file = sys.argv[1]
    rt = RoomThread(Room(json_file))
    ct = ConnectionThread(rt, host, port)
    ct.start()

if __name__ == '__main__':
    main()

