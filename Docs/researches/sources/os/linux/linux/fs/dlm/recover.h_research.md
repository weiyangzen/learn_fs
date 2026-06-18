# File Research: sources/os/linux/linux/fs/dlm/recover.h

## Role

`recover.h` declares recovery wait, status, master recovery, lock recovery, LVB/resource finalization, and inactive cleanup APIs.

## Research Notes

Read completely. The header is the shared contract between `recover.c`, `recoverd.c`, `rcom.c`, `member.c`, and lock receive paths.
