# File Research: sources/os/bsd/dragonflybsd/sys/sys/md4.h

Kernel-only MD4 interface. Userland is explicitly directed to OpenSSL’s MD4 header. Defines `MD4_CTX` with state, count, and input buffer, plus `MD4Init`, `MD4Update`, and `MD4Final`.

Likely used by legacy protocols or compatibility code needing MD4 in kernel context.
