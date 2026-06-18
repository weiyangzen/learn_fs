# File Research: sources/os/plan9/9front/sys/src/cmd/ip/pppoe.c

This is a user-level PPPoE client for RFC 2516. It performs PPPoE discovery over Ethernet, establishes a session, bridges session payloads to a pipe, and execs `/bin/ip/ppp` on that pipe.

It defines Ethernet, PPPoE, and tag headers plus constants for discovery/session ethertypes, discovery codes, and standard tags. `padi` constructs Active Discovery Initiation packets; `padr` constructs Active Discovery Request packets including service name, access concentrator name, and optional cookie.

`pppoe` opens discovery and session Ethernet endpoints, sends PADI/PADR with exponential timeouts, accepts offers and confirmations through `wantoffer` and `wantsession`, and then forks bridge processes. One process copies PPPoE session payloads from Ethernet to the PPP pipe, another wraps PPP bytes from the pipe into PPPoE session frames, and another waits for PADT termination. With `-r`, failed sessions are retried in the background.

`execppp` builds PPP arguments for MTU, primary mode, compression flags, network mount point, IP net names, auth keyspec, DUID, and disables PPP’s own address/control framing with `-F`.

The parser includes validation helpers `malformed`, `findtag`, `dumppkt`, and `dumptags`. DUID-LL is generated from the local Ethernet address when not provided.
