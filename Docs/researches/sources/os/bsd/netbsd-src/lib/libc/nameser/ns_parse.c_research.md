# File Research: sources/os/bsd/netbsd-src/lib/libc/nameser/ns_parse.c

Read completely: 285 lines.

This file parses DNS messages into `ns_msg`, `ns_rr`, and `ns_rr2` views. It defines `_ns_flagdata`, `ns_msg_getflag`, `ns_skiprr`, `ns_initparse`, `ns_parserr`, and `ns_parserr2`.

`ns_initparse` reads the DNS header, records section counts and starting offsets, skips each section to validate message shape, and rejects trailing data. `ns_parserr` parses one resource record into presentation-format owner names via `dn_expand`; `ns_parserr2` parses into uncompressed network-format names via `ns_name_unpack2`. Question-section records omit TTL/RDATA, while other sections parse TTL, RDLENGTH, and RDATA pointers.

Important interactions: this is the structured reader used by resolver clients that need sequential or indexed RR access. It depends on `ns_name` routines for name skipping/unpacking and on nameser byte-order macros for fixed fields.

Security/reliability notes: section and RR index validation return `ENODEV`, and malformed/truncated packets return `EMSGSIZE`. The parser keeps RDATA as pointers into the original message buffer, so the caller must keep that buffer alive.
