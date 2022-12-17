from threads import *

def main():
    # host = sys.argv[1]
    # port = int(sys.argv[2])

    host = '192.168.1.103'                  # sala 1 rasp42
    port = 34315
    server = ServerRecvThread(host, port)
    server.start()
    

if __name__ == '__main__':
    main()
