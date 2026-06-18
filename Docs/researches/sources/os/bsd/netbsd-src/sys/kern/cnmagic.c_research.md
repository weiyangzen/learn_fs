# File Research: sources/os/bsd/netbsd-src/sys/kern/cnmagic.c

## Purpose
Implements console magic-key sequence encoding/decoding as a compact state machine.

## Main Interfaces
- `cn_init_magic()` initializes a `cnm_state_t` to use the global magic table.
- `cn_destroy_magic()` clears the state.
- `cn_set_magic()` parses an escaped magic string into `cn_magic[]`.
- `cn_get_magic()` reconstructs the escaped magic string from the state table.

## Implementation Notes
State entries pack the expected character and next state with `ENCODE_STATE()`. The escape byte `0x27` represents literal escape, BREAK, and NUL encodings.

## Dependencies
Uses console magic constants/macros such as `CNS_LEN`, `CNC_BREAK`, `CNS_TERM`, `CNS_MAGIC_NEXT`, and `CNS_MAGIC_VAL` from kernel headers.
