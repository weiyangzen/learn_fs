# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_stdia.c

Unbuffered stdin reader for platforms supporting `read`.

Key behavior:
- Implements `gp_stdin_read` by calling `read(fileno(f), buf, len)`.
- Ignores the `interactive` flag because unbuffered reads are available.

Notable dependencies:
- `unistd_.h` and standard file descriptors.

Research notes:
- Intended for console input and pipes where buffered stdio behavior is undesirable.
