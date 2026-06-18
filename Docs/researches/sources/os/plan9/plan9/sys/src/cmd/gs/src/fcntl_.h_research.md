# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/fcntl_.h

Portable wrapper for `fcntl.h` open flags.

Key points:
- Includes Ghostscript `std.h` before `<fcntl.h>`.
- Maps Microsoft-style `_O_*` constants to standard `O_*` names when missing:
  - `O_APPEND`, `O_BINARY`, `O_CREAT`, `O_EXCL`
  - `O_RDONLY`, `O_RDWR`, `O_TRUNC`, `O_WRONLY`

Dependencies and interactions:
- Used by code that wants portable `open` mode flags.

OS/filesystem relevance:
- Directly supports portable low-level file opening.
