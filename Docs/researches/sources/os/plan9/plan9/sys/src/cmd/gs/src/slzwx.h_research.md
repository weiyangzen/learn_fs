# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/slzwx.h

Shared LZW encode/decode stream state and templates.

Key contents:
- Forward declares decode and encode table types.
- Defines `stream_LZW_state` with client parameters (`InitialCodeLength`, `FirstBitLowOrder`, `BlockData`, `EarlyChange`) and dynamic bit/dictionary/copy state.
- Defines default parameter macro: initial code length 8, high-bit-first, no block data, early change 1, cleared table pointer.
- Declares encode/decode templates and shared default/release procedures.

Notable dependencies:
- Requires stream implementation context from `strimpl.h`.

Research notes:
- The shared state supports both decoder and encoder even though some parameters are decode-only.
