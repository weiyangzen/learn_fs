# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/disk/mkscsierrs

Read fully: 32 lines, 419 bytes. SHA-256 prefix: `a3d0fe841c9a4dc1`.

This `rc` script generates C source for SCSI error-code lookup. It emits includes, an `Err` table, reads `/sys/lib/scsicodes` lines matching four hex digits, transforms them into `{0xNNNN, "message"}` rows, and emits `scsierrmsg()`.

Integration: supports `scsireq.c::scsierr()` diagnostics. The generated table is not present in this source file; it depends on the system scsi code database at generation time.

Risk notes: generation uses `grep` and `sed` over a system file. Output quality depends on `/sys/lib/scsicodes` format matching the hard-coded expression.
