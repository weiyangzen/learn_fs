# File Research: sources/os/linux/linux/io_uring/truncate.h

Header for io_uring ftruncate support.

Exports:
- `io_ftruncate_prep()`.
- `io_ftruncate()`.

Role:
- Connects ftruncate opcode dispatch to prep and issue handlers.
