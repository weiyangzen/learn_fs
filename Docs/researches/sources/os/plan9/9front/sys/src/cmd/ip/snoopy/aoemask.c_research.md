# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/aoemask.c

This module decodes AoE mask command payloads. It filters on command, error, and count, and demuxes command values 0 and 1 to `aoemd`.

`p_seprint` prints command name, error name, and count. The command table maps values to read/edit; the error table maps values to bad/full.

Notable implementation detail: in `p_seprint`, the error-name assignment writes to `s` rather than `t`, so printed error text may not match the intended table. The module also compiles comparison filters using `aoerr.name`, likely a copy/paste mistake, though runtime behavior depends on shared compile helpers.
