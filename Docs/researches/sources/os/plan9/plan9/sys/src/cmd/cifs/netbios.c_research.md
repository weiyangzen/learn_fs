# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/netbios.c

NetBIOS support for CIFS fallback and debugging. Provides endian helpers, NetBIOS name encoding, adapter-status lookup for the called name (`calledname`), session establishment on TCP/139 (`nbtdial`), NetBIOS session packet headers (`nbthdr`), and RPC send/read framing (`nbtrpc`).

Handles positive/negative session responses, retarget packets, keepalives, MTU checks, alarms/timeouts, and packet hex dumps. `xd` can dump raw packets, decode SMB/Trans2 headers, and log to `pkt.log` when debugging requests it.
