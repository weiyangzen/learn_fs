# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/dump.c

This is the fallback leaf printer for raw payload bytes. It has an empty compile hook and no filter hook.

`p_seprint` limits output length to global `Nflag`. If all selected bytes are printable or whitespace, it emits a string form with tab, carriage return, and newline escaped. Otherwise it emits lowercase hex bytes. It sets `m->pr = nil`.

This module is used as the default demux target throughout snoopy.
