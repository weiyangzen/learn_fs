# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpfmt.c

Formats multiprecision integers as strings.

Key functions:
- `to64`, `to32`, `to16`, `to10`: base-specific conversion helpers.
- `mpfmt`: `Fmt` callback using precision as base selector.
- `mptoa`: public conversion to allocated or caller-provided string buffer.

Important behavior:
- Base 64/32 rely on libsec encoders after big-endian conversion.
- Base 10 repeatedly divides by one billion and emits zero-padded chunks.
- Default base is 16.
