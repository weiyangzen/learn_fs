# File Research: sources/os/bsd/dragonflybsd/sys/sys/bootmaj.h

Read completely: 28 lines.

This header defines legacy boot major-number translation constants.

Key contents:
- Legacy major numbers for wd, wfd, fd, da, scsicd, and mcd boot devices.
- Character device major numbers for corresponding device classes.
- `BOOTMAJOR_CONVARY` initializer mapping old boot majors to current character-device majors or `-1`.

Security/reliability notes:
- No runtime logic. This is boot compatibility data for translating historical block-device major numbers after block devices were removed.
