# File Research: sources/os/bsd/netbsd-src/lib/libc/net/base64.c

Read completely: 350 lines.

This file implements resolver base64 conversion: `b64_ntop` encodes binary data into padded base64 text, and `b64_pton` decodes base64 text into bytes while accepting whitespace.

Encoding processes 3-byte groups, pads 1- or 2-byte tails, checks target capacity before each 4-character write, and NUL-terminates the output. Decoding uses a four-state machine, validates alphabet membership, handles `=` padding rules, skips whitespace, and rejects non-zero unused trailing bits.

Important interactions: `ns_print.c` uses `b64_ntop` to print DNSSEC and other binary RDATA fields.

Security/reliability notes: short target buffers return `-1`; invalid input returns `-1`. The decoder’s unused-bit check closes a classic base64 subliminal-channel/canonicalization issue.
