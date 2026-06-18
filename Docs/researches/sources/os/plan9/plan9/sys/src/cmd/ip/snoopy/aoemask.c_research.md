# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/aoemask.c

`snoopy` decoder for AoE mask command wrapper.

Key behavior:
- Parses reserved byte, mask command, error, and count.
- Filters on command, error, or count.
- Demuxes command values `0` and `1` to `aoemd`.
- Formats command/error/count with small textual tables.

Integration:
- Selected by `aoe.c` command demux value `2`.

Risks and notes:
- `p_compile()` calls `compile_cmp(aoerr.name, ...)`, likely copy/paste error; should refer to `aoemask`.
- In `p_seprint()`, error-name assignment writes into `s` instead of `t`, so error label can corrupt command label.
