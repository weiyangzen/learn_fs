# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/util.c

Utility layer for `cifsd`: logging, remote endpoint reading, path construction/splitting, hex dumps, DOS date/time and Windows FILETIME conversion, allocation rounding, SMB/DOS file attribute mapping, and case-insensitive name hashing.

The string packing/unpacking helpers encode and decode SMB 8-bit and UTF-16LE strings, including optional terminators, alignment padding, surrogate handling, and name translation between SMB backslashes and Plan 9 slashes. Space-to-nonbreaking-space translation is gated by `trspaces`.

Exports the pack/unpack adapter functions used by the SMB packing format engine, including normal strings, file names, and unterminated variants.
