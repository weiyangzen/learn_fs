# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/errstr.h

Static error-string table for `dossrv`.

Key behavior:
- Maps internal error enum values such as `Eformat`, `Eio`, `Enoauth`, `Enonexist`, `Eperm`, `Econtig`, `Ebadstat`, `Etoolong`, and `Eversion` to 9P-facing error text.
- Used by `xerrstr()` in `xfssrv.c`.

Filesystem relevance:
- Defines client-visible failures for FAT parsing, permissions, allocation, protocol, and backing I/O errors.
