# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/mkkeysym.sh

Generates `keysym.h` from `dev/wscons/wsksymdef.h`.

Key behavior:
- Uses `awk`.
- Reads only definitions inside `/*BEGINKEYSYMDECL*/` and `/*ENDKEYSYMDECL*/`.
- Emits encoding constants, `struct ksym`, and `ksym_tab_by_name[]`.
- Strips `KS_` from emitted names.
- Classifies encodings by symbol prefix: `KS_L2_`, `KS_L5_`, `KS_L7_`, `KS_Cyrillic_`; defaults to ISO.

Filesystem/OS relevance:
- Build-time bridge from kernel wscons key symbol definitions to userland lookup tables.
