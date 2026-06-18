# File Research: sources/os/plan9/9front/sys/src/cmd/7l/bits.c

ARM64 logical-immediate lookup support for the `7l` linker/assembler backend.

This file is dominated by the static `bitmasks[]` table, containing encodable ARM64 logical-immediate patterns with their decoded fields:
- `s`: run size/width metadata used by logical-immediate encoding.
- `e`: element size.
- `r`: rotation.
- `v`: the actual 64-bit mask value.

The only function is `findmask(uvlong v)`, which binary-searches `bitmasks[]` and returns the matching `Mask*` or `nil`. It is used by instruction encoding paths to decide whether a constant can be emitted as an ARM64 bitmask immediate.

Important details:
- The table is sorted by `v`, which is required by `findmask`.
- Supports both 32-bit-replicated and full 64-bit encodable logical-immediate forms.
- This is linker backend infrastructure, not filesystem logic.

Filesystem relevance: indirect. It is part of the Plan 9/9front ARM64 toolchain sources included in the OS source tree.
