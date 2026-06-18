# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/trampoline.c

Bidirectional connection relay. It connects stdin/stdout or an alternate dialed address to a target address, then copies data in both directions.

Options:
- `-9`: copy 9P messages atomically by reading the 4-byte length and forwarding complete messages.
- `-a addr`: use a dialed alternate address instead of stdin/stdout for one side.
- `-m netdir`: verify remote MAC address through ARP/NDB before relaying.

Core behavior:
- Dials target address.
- Forks into two copy loops, one per direction.
- Uses `postnote(PNGROUP, getpid(), ...)` to terminate the process group when one side exits.
- `iptomac()` scans `<net>/arp`.
- `macok()` checks NDB for `ether=<mac> trampok`.

Dependencies and integration:
- Uses Plan 9 network dialing, NDB, bio, and fcall length macros.
- Intended as a network service helper/gate.

Notable risks:
- MAC verification is local ARP/NDB based and only as trustworthy as local network state.
- The process-group termination note text is intentionally crude and operationally significant.
- `freeendpoints()` does not free `ep->net`.
