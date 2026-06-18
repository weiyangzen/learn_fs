# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/testppp.c

This is a small PPP test harness. It creates two pipes, starts one PPP process as a server on `/net` and one as a client on `/net.alt`, then shuttles bytes between them.

`pppopen` forks and execs the selected PPP binary, building arguments for debug, server/client mode, no-auth, framing, compression flags, MTU, network mount point, proxy, and local/remote addresses.

`xfer` forwards data from one pipe endpoint to the other. It can inject byte corruption with `-e errrate`, drop whole chunks with `-d droprate`, and optionally print packet prefixes when debug is high. This makes it useful for exercising PPP retransmission, FCS rejection, and compression-reset behavior.

The program expects exactly local and remote address arguments. It is not a protocol implementation itself; it is a local impairment harness for the PPP executable.
