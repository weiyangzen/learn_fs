# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/smtf.c

Implements Move-To-Front encode and decode filters.

Key points:
- Initialization fills the 256-byte previous-symbol list with identity ordering.
- Encoder searches for each input byte in the current list, outputs its index, and moves that byte to the front.
- Decoder maps each input index back to a byte and moves that byte to the front.
- Decode path optimizes common small indices, especially zero, with cached local entries and chunked movement for larger indices.
- Decode template provides reinitialization support.

Dependencies and interactions:
- State layout comes from `smtf.h`.
- Used by Burrows-Wheeler-style or related compression pipelines where move-to-front coding is useful.

Research relevance:
- Simple adaptive symbol-ranking transform filter.
