# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzstdio.c

Small stdio helper module for the split bzip2 library. It implements `bz_feof(FILE*)` by attempting `fgetc`, returning true on `EOF`, otherwise pushing the byte back with `ungetc`.

This is used by `bzread.c` to distinguish depleted input buffers from true file EOF. The implementation is intentionally simple and avoids relying directly on stdio `feof` state before attempting a read.
