# File Research: sources/os/plan9/9front/sys/src/cmd/sha1sum.c

Purpose: Computes SHA-1 by default or SHA-2 digests with `-2 bits`.

Behavior:
- Supported SHA-2 widths: 224, 256, 384, 512.
- Installs `%M` formatter to print digest bytes as lowercase hex.
- Reads stdin if no files are given; otherwise prints digest and filename per file.
- Tracks first error text in `exitstr` and exits with that string if any error occurred.

Integration: Uses `libsec` digest functions.

Risks:
- Continue-on-error for files; exit status carries last stored error string.
- Digest buffer sized for SHA-512 maximum.
