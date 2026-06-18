# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sbcp.c

Implements BCP and TBCP encode/decode filters. Encoding escapes selected control characters by emitting Ctrl-A and XORing the control byte with `0x40`; TBCP escapes a slightly different set.

Decoding recognizes escaped control sequences, end-of-file Ctrl-D, interrupt Ctrl-C, status Ctrl-T, flow-control bytes, and tagged mode additions. Interrupt and status handling are callback hooks stored in the decode state. The code is stream-resumable through `escaped`, `copy_count`, and related fields, although copy-string support is effectively dormant here.

Dependencies include `strimpl.h` and `sbcp.h`. It exports templates for `BCPEncode`, `TBCPEncode`, `BCPDecode`, and `TBCPDecode`.

Filesystem relevance is indirect: BCP/TBCP is printer/job transport encoding for userland Ghostscript streams.
