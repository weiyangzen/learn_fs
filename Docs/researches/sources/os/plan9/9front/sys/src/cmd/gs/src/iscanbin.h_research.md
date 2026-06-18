# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iscanbin.h

Declares the internal binary-token scanner entry point `scan_binary_token`. The main scanner calls it only when binary tokens are enabled and recognized.

The header notes that it exists because Ghostscript can provide either a real Level 2 implementation or a dummy Level 1 implementation. Its return contract mirrors scanner conventions: `0` or `scan_BOS` on success, negative errors on failure, and `scan_Refill` for resumable input.
