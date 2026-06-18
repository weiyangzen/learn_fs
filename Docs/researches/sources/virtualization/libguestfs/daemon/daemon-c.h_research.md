# File Research: sources/virtualization/libguestfs/daemon/daemon-c.h

Header for C/OCaml bridge functions.

Key points:
- Includes `daemon.h` plus OCaml `mlvalues.h`.
- Declares exception translation, mountable conversion, string-list conversion, and hashtable return conversion helpers.
- Kept separate from `daemon.h` to avoid exposing OCaml headers across the daemon.
