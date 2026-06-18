# sources/security-integrity/cryfs/crates/utils/src/testutils/data_fixture.rs

Purpose: Implements `DataFixture`, a reproducible pseudo-random byte stream generator for tests that can efficiently fill arbitrary offsets without generating all preceding bytes.

Important APIs and types: `DataFixture::new(seed)`, `generate(offset, dest)`, and `get(size)` are the public surface. Private helpers include `generate_block` and `subslices`. The fixed block size is 2 KiB.

Control flow: Construction runs the user seed once through `SmallRng` so nearby seeds diverge before block-index arithmetic is used. `generate` computes the start and end block indices for the requested offset/length, splits the destination into a possibly short first slice and full-size following slices, then uses Rayon parallel iteration to fill each slice. `generate_block` seeds `SmallRng` with `self.seed + block_index`, generates enough bytes rounded up to an 8-byte multiple, and copies the requested in-block range. `get` allocates a vector and calls `generate(0, ...)`.

State and persistence behavior: The only persistent object state is the derived seed. Generated data is deterministic for a given seed, offset, and length, regardless of how requests are chunked. No files or global state are touched.

Dependencies and integration points: Depends on `rand::SmallRng`, `SeedableRng`, `Rng`, `divrem::DivCeil`, and `rayon`. It is a test utility for storage, block, stream, and encryption-style tests that need repeatable nontrivial data.

Risks: Parallel fill is deterministic because each block has its own seed, but it still depends on exact `SmallRng` algorithm stability for byte-for-byte fixtures. `generate_block` allocates a temporary vector per block and rounds to 64-bit fill granularity. `subslices` always returns a first slice, including an empty first block when the requested first block size is zero; current callers avoid problematic non-empty zero-first cases. Assertions guard invalid internal offsets.

Test signals: Tests verify different seeds differ, same seeds match, empty and one-byte generation, expected count of zero bytes in 1 MiB, many section sizes producing the same output as one whole generation, `get(0)`, one-byte `get`, and `get` matching `generate`.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/src/testutils/data_fixture.rs` completely for this pass (275 lines, 10201 bytes).
