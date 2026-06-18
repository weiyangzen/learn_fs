# sources/test-tools/fio/lib/ieee754.h

Purpose: exposes IEEE-754 packing helpers and fio's portable 64-bit floating storage type.

Important APIs/types: `pack754`, `unpack754`, macros `fio_double_to_uint64` and `fio_uint64_to_double`, and `fio_fp64_t`, whose union provides a `uint64_t`, `double`, and padding bytes.

Control flow/state: no state in the header. Callers use macros for double conversion or store means/statistics in `fio_fp64_t`.

Dependencies/integration: includes fixed-width integer types. `iolog.h` and stats code use `fio_fp64_t` to keep alignment and serialization predictable.

Risks/test signals: native union access and explicit pack/unpack are different paths; tests should ensure the selected path preserves values and alignment on strict architectures.
