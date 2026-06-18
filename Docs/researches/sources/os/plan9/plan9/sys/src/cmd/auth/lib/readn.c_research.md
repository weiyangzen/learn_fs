# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/readn.c

Defines a small exact-read helper. It loops until `len` bytes have been read or a read returns zero/error, returning `-1` on short read.

Used by auth protocol code that needs fixed-size records.
