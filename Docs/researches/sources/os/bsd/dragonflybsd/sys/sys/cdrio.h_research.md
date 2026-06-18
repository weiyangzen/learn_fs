# File Research: sources/os/bsd/dragonflybsd/sys/sys/cdrio.h

CD-R/CD-RW writer ioctl ABI for blanking, track setup, cue sheets, fixation, speeds, block size, and progress.

Key responsibilities:
- Defines `struct cdr_track` with data block type, preemphasis, and test-write flags.
- Defines raw, subchannel, Mode 1/2, XA, reserved, and vendor-specific data block type constants.
- Defines cue sheet entry and session format/type structures.
- Defines ioctls for blanking media, querying next writable address, initializing writer/track, sending cue sheets, flushing, fixating, setting read/write speeds, getting/setting block size, and querying progress.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.

Notable risks:
- `struct cdr_cuesheet` contains a user pointer to cue entries; ioctl handlers must validate length and copy safely.
- Session and data block constants are protocol-facing and must match ATAPI/SCSI driver expectations.
