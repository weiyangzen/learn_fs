# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/smtf.h

Defines Move-To-Front filter state and templates.

Key points:
- `stream_MTF_state` stores the dynamic 256-entry previous-symbol table as either bytes or longs for optimized movement.
- Typedefs the shared state as both encode and decode state.
- Declares encode/decode stream templates.

Research relevance:
- Header contract for the MTF transform filters.
