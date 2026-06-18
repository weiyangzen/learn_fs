# File Research: sources/os/plan9/plan9/sys/src/cmd/samterm/mesg.c

Implements the terminal side of the `sam` protocol.

Key responsibilities:
- `rcv` parses host-originated `Hmesg` records and dispatches `inmesg`.
- Handles host messages for version, names, current file, grow/cut/data, check/request flow, unlock, setdot, origin, move-to, clean/dirty, snarf, ack, exit, and plumb.
- Serializes terminal-originated `Tmesg` records through `outT*` helpers.

Key functions:
- `setlock`/`clrlock` update host lock state and cursor.
- `startfile` and `startnewfile` initiate host binding for terminal text.
- `hsetdot`, `horigin`, `hmoveto`, `hcheck`, `hgrow`, `hdata`, `hdatarune`, and `hcut` mutate local rasps and flayers.
- `hsetsnarf` swaps with `/dev/snarf`; `hplumb` unpacks and stores plumb messages.

Behavior notes:
- `Hcheck` scans visible flayers for missing data and sends `Trequest` for holes.
- `Hgrowdata` folds a resize and data payload into one terminal update.
- Terminal locks defer local edits while host-side commands are in progress.
