# File Research: sources/os/linux/linux/io_uring/query.h

Header for the io_uring query registration helper.

Key responsibilities:
- Declares `io_query()` for dispatch from `register.c`.
- Includes io_uring type definitions needed for user pointer handling.

Important invariant:
- Query is a registration-style operation and is also allowed as a blind operation without a ring fd.
