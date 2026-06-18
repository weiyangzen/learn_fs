# File Research: sources/os/plan9/9front/sys/src/cmd/ip/pptp.c

This is a PPTP client that negotiates the PPTP TCP control channel, establishes a GRE PPP tunnel, and runs `/bin/ip/ppp` over a local pipe.

`threadmain` parses primary/debug/keyspec/window/network options, dials the server, and calls `pushppp`. `pptp` dials TCP service `pptp`, reads local/remote addresses from the dial directory, starts the control reader, sends Start-Control-Connection and Outgoing-Call requests, opens a GRE endpoint, then starts GRE reader, PPP reader, and timeout processes.

`pptpctlproc` reads length-prefixed PPTP control messages, validates magic/type, handles peer echo requests, rejects unexpected control operations, and delivers expected responses through a channel. `tstart` and `tcallout` construct client control messages and validate returned control replies.

GRE handling uses PPTP GRE protocol `0x880B`. `pppreadproc` wraps PPP bytes with source/destination IPv4 addresses, GRE flags, call id, sequence, and ACK. `grereadproc` validates source/destination/protocol, extracts ACK and sequence fields, and forwards in-order PPP payloads to the PPP pipe. `schedack`, `sendack`, `recordack`, and `waitacks` implement basic sequencing and acknowledgment behavior, with a small out-of-order swap recovery path.

`gretimeoutproc` advances ticks, sends control-channel echo requests, and fails on server timeout. `myfatal` tries to send a PPTP Stop-Control-Connection request before terminating all threads.
