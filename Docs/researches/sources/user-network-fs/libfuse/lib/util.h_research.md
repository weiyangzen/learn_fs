# sources/user-network-fs/libfuse/lib/util.h

## Purpose
Shared libfuse utility header with numeric helpers, branch prediction macros, container helpers, fallthrough annotation, and rounding functions.

## Important APIs, Types, And Functions
- Macros: `max`, `min`, `ROUND_UP`, `likely`, `unlikely`, `FUSE_VAR_UNUSED`, `container_of`, `fallthrough`.
- Inline helpers: `fuse_lower_32_bits`, `fuse_higher_32_bits`, `round_up`, `round_down`, and `howmany`.
- Declares `libfuse_strtol` and `fuse_set_thread_name`.

## Control Flow
Only inline utility logic. Rounding helpers explicitly return input unchanged for `align == 0`.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Included broadly by libfuse library and utility code. `container_of` assumes `offsetof` is visible to includers or included before use.

## Risks
`max` and `min` evaluate arguments multiple times. `ROUND_UP` assumes power-of-two alignment due to bit masking. `fuse_higher_32_bits` returns the high-bit mask, not a shifted high 32-bit value, which callers must understand.

## Test Signals
Compile with compilers lacking `__fallthrough__`, test rounding with zero/non-power-of-two alignments, and audit macro call sites for side effects.
