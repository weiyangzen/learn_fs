# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclfile.c

Filesystem-backed implementation of the command-list I/O interface. `clist_fopen` opens an existing file or creates a scratch file when the name buffer is empty; reading with an empty name is rejected. `clist_fclose` closes and optionally unlinks the file, while `clist_unlink` wraps `unlink`.

The write/read API is thin stdio: `clist_space_available` reports the requested amount, `clist_fwrite_chars` writes bytes with `fwrite`, and `clist_fread_chars` uses an optimized fall-through `getc` path for reads of 1 to 8 bytes to avoid small `fread` overhead. Status and positioning wrappers expose memory-warning no-op behavior, `ferror`, `ftell`, rewind, truncating rewind via `freopen`, and `fseek`. This is the portable file-system counterpart to any RAM-backed clist I/O implementation.
