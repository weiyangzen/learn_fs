# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/disk/mkscsierrs

This rc script generates a C source fragment containing SCSI additional sense-code messages. It emits includes, an `Err` struct, a `scsierrs[]` table, and a `scsierrmsg(int)` lookup function.

The table is generated from `/sys/lib/scsicodes`. Lines beginning with four lowercase hexadecimal characters followed by whitespace are transformed by `sed` into `{0xCODE, "message"}` entries. The generated lookup returns the matching message or the generic string `"scsi error"`.

The generated function is referenced by `scsireq.c` through the declaration in `scsireq.h`, allowing USB disk diagnostics to report textual SCSI sense errors without depending on libdisk.
