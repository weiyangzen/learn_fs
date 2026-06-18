# File Research: sources/os/linux/linux/io_uring/fdinfo.h

## Purpose
Declares the io_uring fdinfo display hook.

## Main Contents
- Prototype for `io_uring_show_fdinfo()`.

## Cross-File Relationships
- Implemented by `fdinfo.c`.
- Hooked through io_uring file operations when proc fdinfo is available.

## Risks / Review Notes
- Minimal header with no guard; include usage is local and simple.
