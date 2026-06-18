# File Research: sources/os/linux/linux/io_uring/epoll.h

## Purpose
Declares io_uring epoll opcode handlers when epoll support is enabled.

## Main Contents
- Under `CONFIG_EPOLL`, prototypes for epoll ctl prep/issue and epoll wait prep/issue.

## Cross-File Relationships
- Implemented by `epoll.c`.
- Included by opcode dispatch definitions.

## Risks / Review Notes
- No disabled-config stubs are provided here; callers must be config-aware.
