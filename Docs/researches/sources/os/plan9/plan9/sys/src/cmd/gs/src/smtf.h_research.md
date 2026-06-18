# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/smtf.h

Header for MoveToFront encode/decode filters.

Key contents:
- Defines `stream_MTF_state` with a 256-byte previous-symbol list stored as a union of bytes and machine words.
- Aliases encode and decode state types to the same structure.
- Declares GC structure macro and stream templates.

Notable dependencies:
- Requires stream common definitions.

Research notes:
- The union supports the word-sized shifting optimization in the decoder.
