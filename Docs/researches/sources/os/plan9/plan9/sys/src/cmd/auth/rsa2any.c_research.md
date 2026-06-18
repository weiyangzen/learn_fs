# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/rsa2any.c

Shared RSA/DSA key parser and SSH-style binary encoding helpers. `getkey` reads a factotum `key proto=rsa ...` line, parses public/private mpints, validates/corrects `size`, and regenerates CRT fields with `rsafill` when missing or malformed.

`getdsakey` parses `proto=dsa` keys with public `p`, `q`, `alpha`, `key` and private `!secret`. Both functions return remaining non-key attrs through `pa`.

`put4`, `putn`, `putstr`, and `putmp2` serialize fields for SSH-compatible buffers, including positive mpint leading-zero handling.
