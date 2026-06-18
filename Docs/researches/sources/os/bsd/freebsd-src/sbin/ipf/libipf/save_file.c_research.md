# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/save_file.c

`ipmon` file saver backend.

Key behavior:
- Registers `filesaver`.
- Parses `raw://path` for binary append and `file://path` for text append.
- Supports matching and reference-counted duplication for shared file contexts.
- Writes raw data or formatted message text in `file_send()`.

Research notes:
- `file_destroy()` frees path/context but does not close `fp`.
