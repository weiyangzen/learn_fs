# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxsample.h

`gxsample.h` declares lookup data and sample-unpack procedures for image decoding.

`sample_lookup_t` is a union of lookup-table layouts: 4x1-to-32-bit expansion for 1-bit samples without spreading, 2x2-to-16-bit expansion for 2-bit samples without spreading, and byte lookup for spread or higher-bit cases. The header declares identity and inverted 1-bit expansion tables.

`sample_map` is forward-declared. The `SAMPLE_UNPACK_PROC` macro defines the common unpacker signature. Unpackers receive an output buffer, output sample offset pointer, source data and bit/sample offset, source data size, sample map, spread factor, and number of components per plane. They return either the provided buffer or the original data pointer.

Declared unpackers include `sample_unpack_copy`, 1/2/4/8-bit unpackers, and interleaved 1/2/4/8-bit variants. This API supports efficient image data preparation before rendering.
