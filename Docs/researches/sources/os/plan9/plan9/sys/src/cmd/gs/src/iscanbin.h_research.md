# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iscanbin.h

Purpose: declares the internal binary-token scanner entry point `scan_binary_token`.

The main scanner calls this only when binary tokens are enabled by the binary object format and Level 2 support. The header exists because builds may provide either the real Level 2 implementation or a dummy Level 1 implementation.

Return contract: 0 for a normal binary token, `scan_BOS` for a binary object sequence, `scan_Refill` when more input is required, or a negative Ghostscript error code.
