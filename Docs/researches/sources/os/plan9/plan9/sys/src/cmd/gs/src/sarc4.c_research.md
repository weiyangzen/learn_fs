# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sarc4.c

Arcfour stream cipher implementation used by Ghostscript filters.

The file implements an RC4-compatible symmetric byte stream, described as based on Schneier’s presentation and functionally equivalent to RC4 as referenced by PDF.

Important routines:

- `s_arcfour_set_key` initializes the 256-byte S-box from a supplied key and rejects empty keys.
- `s_arcfour_process` generates keystream bytes, XORs them with input, and preserves the `x`/`y` indices and S-box between calls.
- `s_arcfour_process_buffer` applies the same transform in-place to a buffer using stream cursors.
- `s_arcfour_template` exposes the filter with byte-sized input/output units.

The same operation encrypts and decrypts. This is cryptographic stream-filter code for document/PDF handling, not filesystem code.
