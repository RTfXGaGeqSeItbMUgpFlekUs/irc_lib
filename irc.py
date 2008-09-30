#!/usr/bin/python
#vim: encoding=utf-8

# Import standard modules
import socket

class IRC:
    ssl = None
    done = False
    parsers = []

    def connect(self, options):
        """
        Connects to an IRC server and initializes the connection.
        
        Required options:
        'server' 'port' 'nickname' 'username' 'realname'
        Other options:
        'password'
        'channels' -- List. Channels to autojoin.
        'ssl' -- Boolean.
        """
        # Initialize the socket.
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((options['server'], options['port']))
        try:
            if options['ssl']: # SSL ftw!
                print 'Congratulations! You have a SSL-encrypted connection.'
                self.ssl = True
                self.ssl_socket = socket.ssl(self.socket)
                print 'Server SSL Certificate:', repr(self.ssl_socket.server())
                print 'Issuer SSL Certificate:', repr(self.ssl_socket.issuer())
                print 'IMPORTANT: If you do not trust the issuer, press \
control-C to disconnect now!'
        except KeyError:
            pass

    def send(self, what):
        """Send data over the socket."""
        if self.ssl:
            self.ssl_socket.write('%s\r\n' % what)
        else:
            self.socket.send('%s\r\n' % what)
        print self.socket.getsockname(), '>', self.socket.getpeername(), \
                '<<<<', what

    def poller(self):
        """Infinite data receiving loop."""
        readbuffer = ''
        while not self.done:
            # Grab data from the socket.
            if self.ssl: readbuffer = readbuffer + self.ssl_socket.read()
            else: readbuffer = readbuffer + self.socket.recv(1024)
            # Get the completed data, and dump the rest into the readbuffer.
            temp = readbuffer.split('\r\n')
            readbuffer = temp.pop()
            # Separate the data into lines.
            for line in temp:
                print self.socket.getsockname(), '<', \
                        self.socket.getpeername(), '>>>>', line
                # Parse the data.
                for parser in self.parsers:
                    parser(self, line)

    def add_parser(self, parser):
        self.parsers.append(parser)

def myparser(irc, what):
    # Not real code, just helper functions until I write the real code.
    _what = what.split()
    if _what[0] == 'PING':
        irc.send('PONG %s' % _what[1])
    if _what[1] == 'PRIVMSG' and _what[3] == ':TALK!!!':
        irc.send('PRIVMSG %s :hi?' % _what[2])
    if _what[1] == 'PRIVMSG' and _what[3] == ':QUIT!!!':
        irc.send('QUIT :bye')
        irc.done = True

if __name__ == '__main__':
    irc = IRC()
    irc.connect({'server': 'irc.freenode.net', 'port': 6667})
    irc.send('NICK sdkmvxbot')
    irc.send('USER sdkmvxbot - - :sdkmvx')
    irc.send('JOIN #botters')
    irc.add_parser(myparser)
    irc.poller()
    if irc.ssl: del irc.ssl_socket
    irc.socket.close()
    print 'bye'
