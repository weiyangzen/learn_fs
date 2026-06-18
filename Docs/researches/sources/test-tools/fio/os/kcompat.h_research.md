# sources/test-tools/fio/os/kcompat.h

## Purpose
`kcompat.h` provides tiny kernel-style integer aliases for fio code or imported headers that expect Linux kernel type names.

## Important APIs, Types, and Functions
It includes `<stdint.h>` and defines `u64` as `uint64_t` and `u32` as `uint32_t`.

## Control Flow
There is no runtime control flow. Inclusion supplies type aliases at preprocessing time.

## State and Persistence
The file has no state and no persistent effects.

## Dependencies and Integration Points
It integrates with source that shares definitions with kernel ABI headers or helper code where `u32`/`u64` naming is expected without pulling in broader kernel headers.

## Risks and Edge Cases
The aliases are macros rather than typedefs, so they can collide if another header has already defined the names differently. It deliberately does not define signed, 8-bit, 16-bit, or endian-qualified variants.

## Test Signals
Compile coverage for files including kernel-compatible ABI definitions is sufficient; no runtime tests are meaningful.
