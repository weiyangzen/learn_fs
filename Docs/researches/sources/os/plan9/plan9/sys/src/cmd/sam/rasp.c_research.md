# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/rasp.c

Maintains the host-side rasp, the compact map of what text the terminal already has.

Key functions:
- `raspload`, `raspstart`, `raspdone`, and `raspflush` bracket batched terminal updates.
- `raspdelete` and `raspinsert` update dot/mark positions, file rasp ranges, and terminal grow/cut/data messages.
- `rcut` removes spans from the rasp piece list.
- `rgrow` inserts not-in-terminal pieces.
- `rterm` checks whether a position is inside terminal-known text.
- `rdata` locates a terminal-missing span to satisfy `Trequest`.

Implementation details:
- Rasp pieces are stored in a `List` of `Posn`; high bit `M` marks text resident in the terminal.
- Large inserts are sent as `Hgrowdata`; smaller terminal-known inserts may be sent as `Hgrow` plus `Hdata`.
- `GROWDATASIZE` controls when grow/data folding is used.

Risk/maintenance notes:
- The piece list encoding is dense and relies on bit masks over signed-looking `Posn` values.
- `raspdone` clamps dot/mark after file-size changes before flushing protocol messages.
