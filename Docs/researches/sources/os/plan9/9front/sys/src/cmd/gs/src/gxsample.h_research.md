# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxsample.h

Sample lookup and expansion interface for image sample unpacking.

Key contents:
- Defines `sample_lookup_t`, a union containing lookup tables for 1-bit-to-32-bit, 2-bit-to-16-bit, and 8-bit byte expansion cases.
- Declares identity and inverted standard 1-bit expansion lookup arrays.
- Defines the `SAMPLE_UNPACK_PROC` macro and `sample_unpack_proc_t` function pointer type.
- Declares no-copy unpacking plus 1-, 2-, 4-, and 8-bit unpackers, including interleaved multi-map variants.

Notable dependencies:
- Expects `bits32`, `bits16`, `byte`, `uint`, and `sample_map` context from surrounding Ghostscript headers.

Research notes:
- Unpacking routines may return either the caller buffer or the original input data, so callers must use the returned pointer rather than assuming `bptr`.
- `spread` and `num_components_per_plane` allow both contiguous expansion and interleaved component layouts.
