# sources/storage-engines/wiredtiger/src/include/intpack_inline.h

## Purpose
Defines WiredTiger's lexicographically ordered variable-length integer encoding for signed and unsigned 64-bit values, plus fixed 32-bit integer packing helpers. The encoding is designed so the byte representation sorts in the same order as the numeric value, which is important for packed keys and other byte-comparable serialized structures.

## Important APIs, Types, And Functions
- Marker and range macros: `NEG_MULTI_MARKER`, `NEG_2BYTE_MARKER`, `NEG_1BYTE_MARKER`, `POS_1BYTE_MARKER`, `POS_2BYTE_MARKER`, `POS_MULTI_MARKER`, `NEG_1BYTE_MIN`, `NEG_2BYTE_MIN`, `POS_1BYTE_MAX`, and `POS_2BYTE_MAX` define the first-byte classes and compact value ranges.
- `GET_BITS` extracts first-byte payload bits; `WT_SIZE_CHECK_PACK` and `WT_SIZE_CHECK_UNPACK` enforce bounded pack/unpack access with different error semantics (`ENOMEM` for insufficient write space, `EINVAL` for malformed/truncated read input).
- `WT_LEADING_ZEROS` has compiler-specific implementations for GCC, MSVC, and a portable fallback.
- `__wt_vpack_uint`, `__wt_vpack_int`, `__wt_vunpack_uint`, and `__wt_vunpack_int` are the primary variable-length integer serialization APIs.
- `__wt_vsize_uint` and `__wt_vsize_int` compute encoded lengths without writing.
- `__wt_pack_fixed_uint32` and `__wt_unpack_fixed_uint32` provide endian-aware fixed-width 32-bit packing.

## Control Flow
Packing first checks for the compact one-byte or two-byte ranges. Values outside those ranges are normalized by subtracting the compact range boundary and delegated to `__wt_vpack_posint` or `__wt_vpack_negint`, which encode a length nibble in the first byte followed by big-endian payload bytes. Signed packing sends non-negative values through the unsigned path and uses separate negative markers for negative values.

Unpacking reads the high nibble of the first byte, dispatches to the matching compact or multi-byte decoder, validates required length before reading, and advances the caller-owned pointer only after the consumed bytes are known. The special unsigned value `POS_2BYTE_MAX + 1` is deliberately encoded as two bytes so encoded size does not shrink at the multi-byte boundary.

## State And Persistence Behavior
The functions are stateless except for advancing caller-supplied buffer pointers. Their output is a persistent on-disk/on-wire encoding contract used by higher-level packing and key serialization. Endianness is normalized for fixed-width 32-bit values under `WORDS_BIGENDIAN`; variable-length integer payloads are written most-significant byte first to preserve lexical ordering.

## Dependencies And Integration Points
This header depends on global WiredTiger error macros (`WT_RET`, `WT_RET_TEST`), constants such as `WT_INTPACK64_MAXSIZE`, byte-swap helpers, and compiler/platform headers for leading-zero intrinsics. It is consumed by `packing_inline.h` for struct format packing and by any code that needs ordered integer byte encodings.

## Risks
The marker ranges and boundary constants are part of persistent data format; changing them would break compatibility or ordering. Length checks treat `maxlen == 0` as unchecked, so callers that parse untrusted buffers must pass real limits. Casting `int64_t *` to `uint64_t *` in signed unpack relies on two's-complement representation and alignment expectations. Compiler-specific leading-zero behavior and GCC warning suppressions need coverage across supported toolchains.

## Test Signals
Useful tests include round-trip and expected-byte tests for all range boundaries, lexicographic ordering comparisons across negative/positive values, malformed/truncated buffer handling, `maxlen` enforcement, big-endian fixed-uint32 behavior, and MSVC/GCC builds for intrinsic paths.
