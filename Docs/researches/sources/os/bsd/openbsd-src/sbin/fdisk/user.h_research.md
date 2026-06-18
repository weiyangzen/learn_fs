# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/user.h

Small fdisk user-interface header declaring:
- `USER_edit` for entering the interactive editor at a given MBR LBA context.
- `USER_print_disk` for noninteractive disk table display.
- `USER_help` for context-sensitive command help.

It depends on `struct mbr` being visible to callers that use `USER_help`.
