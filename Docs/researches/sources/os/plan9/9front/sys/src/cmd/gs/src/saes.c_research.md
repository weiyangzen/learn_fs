# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/saes.c

Implements an AES stream filter wrapper around Plan 9 libsec AES CBC routines. It stores key material in the stream state, delays AES setup until processing begins, reads the first 16 input bytes as the CBC initialization vector, and decrypts full 16-byte blocks.

The process routine supports optional RFC 1423-style padding removal on the final block. It is symmetric at the stream-template level but this implementation calls `aesCBCdecrypt`, so its operational behavior here is decryption. It returns stream suspension when more input or output space is needed.

Dependencies include `saes.h`, `strimpl.h`, Ghostscript error headers, and Plan 9 `<libsec.h>` via the header.

Risk notes: invalid key lengths and missing keys fail; invalid padding is tolerated by treating padding length as zero, matching a bug-compatibility comment. It is cryptographic stream support for PDF/PostScript, not filesystem logic.
