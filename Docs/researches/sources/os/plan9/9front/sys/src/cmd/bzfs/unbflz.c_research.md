# File Research: sources/os/plan9/9front/sys/src/cmd/bzfs/unbflz.c

This implements BLZ expansion as a pipe-producing process.

Behavior:
- Validates `BLZ\n` header.
- Reads uncompressed length as big-endian.
- Reads block descriptors until their summed lengths equal the output length.
- Descriptor high bit means literal data follows; otherwise descriptor is a back-reference with offset.
- Reconstructs the full output in memory, then writes it to the pipe.

Notable implementation details:
- `Bgetint` reads big-endian 32-bit integers from a `Biobuf`.
- `copy` is a forward byte copy intended to make overlapping back-reference expansion work.
- Forks with `RFMEM`, so child shares memory where Plan 9 semantics allow.

Risks and caveats:
- Entire expanded output is allocated at once.
- Corrupt descriptors can reference arbitrary prior offsets; there is no explicit offset bounds check.
