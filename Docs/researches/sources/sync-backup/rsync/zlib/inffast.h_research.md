# sources/sync-backup/rsync/zlib/inffast.h

Purpose: private declaration header for the optimized inflate decoder in `inffast.c`.

Important APIs/types/functions: declares `void ZLIB_INTERNAL inflate_fast OF((z_streamp strm, unsigned start));`. The declaration uses zlib's `OF` compatibility macro and hidden/internal export convention.

Control flow: no runtime logic. Its role is to let `inflate.c` call the fast path when the state machine has enough input and output space.

State and persistence: no state. The declared function mutates `z_stream` and `inflate_state`, but this header only provides the signature.

Dependencies and integration points: relies on `z_streamp` and `ZLIB_INTERNAL` being defined before inclusion, as they are through `zutil.h`/`zlib.h` in the including source. Included by both `inflate.c` and `inffast.c` to keep the prototype consistent.

Risks: signature drift would break ABI-internal calls or assembler replacement compatibility. The `start` parameter is essential for computing the beginning of the output buffer inside `inflate_fast`; removing or changing it would break distance calculations.

Test signals: compilation is the main direct signal. Runtime fast-path coverage in inflate tests indirectly validates that this declaration matches the implementation and call site.
