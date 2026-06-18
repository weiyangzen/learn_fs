# File Research: sources/windows/reactos/drivers/filesystems/btrfs/blake2b-ref.c

Bundled reference C implementation of BLAKE2b hashing, exposed to the driver as a simple one-shot `blake2b()` function.

Key entry points:
- `blake2b()` initializes state, absorbs the input buffer, finalizes, and writes the requested digest length.
- `blake2b_init()` builds a default unkeyed parameter block with fanout/depth set to 1 and zero salt/personalization.
- `blake2b_update()` buffers input, compresses full 128-byte blocks, and leaves the final partial block in state.
- `blake2b_final()` marks the last block, pads the buffer, performs final compression, serializes the 64-byte internal hash, and copies `S->outlen` bytes to the caller output.
- `blake2b_compress()` implements the 12-round BLAKE2b compression function using the IV, sigma schedule, counter, finalization flags, and `G`/`ROUND` macros.

Core mechanics:
- Uses the standard BLAKE2b IV and 12-round message permutation table.
- Maintains a 128-bit byte counter in `S->t[0..1]`.
- Uses `S->f[0]` and `S->f[1]` as final-block and last-node flags.
- Provides unkeyed hashing only; keyed mode and tree hashing are not exposed here.

Filesystem relevance:
- Called from read, write, flush, and calculation paths to verify or compute Btrfs BLAKE2 checksum values for superblocks, tree blocks, and data sectors.

Important invariants:
- `outlen` must be no larger than the BLAKE2b output buffer size; `blake2b_final()` rejects too-small caller output but the one-shot wrapper does not surface errors.
- `blake2b_final()` may only be called once per initialized state.
- Input length is `size_t`, though the comment notes that at least `inlen` should ideally be 64-bit for full generality.

Notable risks:
- The public wrapper ignores return codes from update/final, so invalid digest lengths would fail silently from the caller's perspective.
- The file includes `<stdio.h>` even though the driver implementation does not need formatted I/O here.
- This is generic reference code rather than an optimized or constant-time-tuned kernel implementation; for filesystem checksums, correctness and portability matter more than secrecy.
