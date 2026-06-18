# File Research: sources/os/plan9/9front/sys/src/cmd/md5sum.c

Implements a Plan 9 `md5sum` command compatible with file-list or stdin usage.

Key behavior:
- Installs `%M` formatter to print `MD5dlen` bytes as lowercase hexadecimal.
- Streams each file through `md5()` using `IOUNIT` reads.
- Prints just the digest for stdin, or digest plus tab plus filename for files.
- Accumulates an exit string on read/open errors and exits with that status.

Important dependencies: `libsec` MD5 API, Plan 9 `Fmt`, `IOUNIT`, `ERRMAX`.

Notable risks:
- Continues after open/read failures but final exit status is the last recorded error string.
- Uses MD5 only; this is checksum compatibility, not cryptographic integrity guidance.
