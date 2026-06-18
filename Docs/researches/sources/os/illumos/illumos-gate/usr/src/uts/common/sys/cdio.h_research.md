# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cdio.h

`cdio.h` defines the CD-ROM ioctl ABI and related SCSI command constants. It includes structures for MSF ranges, track/index playback, TOC headers/entries, subchannel data, volume control, raw reads, CD-DA, CD-XA, and subcode reads, with `_SYSCALL32` conversion macros for pointer-bearing forms.

It defines address formats, audio statuses, data/subcode modes, legal block sizes, drive speed constants, `CDROM*` ioctl numbers, optional/vendor SCSI opcodes, READ CD expected sector type constants, and a SCSI command key string table macro for CD I/O debugging.
