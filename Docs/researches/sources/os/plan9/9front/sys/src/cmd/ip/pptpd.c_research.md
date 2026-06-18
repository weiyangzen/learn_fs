# File Research: sources/os/plan9/9front/sys/src/cmd/ip/pptpd.c

This is the PPTP server-side handler. It is intended to be run for an accepted PPTP TCP connection, using the passed TCP dial directory to discover local/remote addresses. It negotiates PPTP control messages, opens a GRE endpoint, allocates per-call PPP sessions, and bridges GRE payloads to `/bin/ip/ppp`.

The central server object `srv` stores connection addresses, GRE fds, PPP executable/net mount settings, receive window, DHCP-derived base address, and a call hash table. Each `Call` stores call id, PPP fd, GRE sequence/ACK/window state, error stats, DHCP pipes, and refs.

`serve` reads control messages from stdin, validates the PPTP magic and type, and dispatches to handlers. Implemented handlers include start, stop, echo, outgoing call, call clear/disconnect, WAN info, and link info. Incoming-call request/connect paths are present but fatal as not implemented.

`callalloc` allocates a call id, obtains a remote IP using `/bin/ip/dhcpclient`, starts `/bin/ip/ppp -SC` with local and remote addresses, inserts the call in the hash table, and starts PPP read and GRE timeout workers.

`greread` parses GRE packets, validates source/destination/protocol/key, finds the call by call id, updates ACKs, forwards in-order PPP payloads, accounts missing/dropped packets, and sends ACKs when the receive window has advanced. `pppread` reads PPP bytes, wraps them in GRE key/seq/ack headers, and waits on an event when the send window is full.

`timeoutthread` closes the server after control-channel inactivity. `myfatal` sends a PPTP stop message, logs through syslog, closes fds, and posts a process-group note.
