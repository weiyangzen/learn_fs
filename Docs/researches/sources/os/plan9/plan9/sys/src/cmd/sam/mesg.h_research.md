# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/mesg.h

Defines the shared `sam`/`samterm` wire protocol.

Key contents:
- `VERSION` is `2`; comments record version 1 plumbing support and version 2 snarf-size expansion.
- `TBLOCKSIZE`, `DATASIZE`, and `SNARFSIZE` define text chunk and protocol buffer limits.
- `Tmesg` enumerates terminal-to-host messages such as `Tstartfile`, `Ttype`, `Tcut`, `Tpaste`, `Tsearch`, `Tplumb`, and `Texit`.
- `Hmesg` enumerates host-to-terminal messages such as `Hbindname`, `Hgrow`, `Hdata`, `Hsetdot`, `Hsetsnarf`, `Hack`, `Hexit`, and `Hplumb`.
- `Header` is the packed protocol header: one-byte type, two-byte little-endian count, and variable data.

Behavior notes:
- The comment includes a Holzmann-style protocol model for grow/data/check/request flow control and notes a non-progress-cycle proof.
- The enum values are positional wire values; host and terminal code must stay in lockstep.
