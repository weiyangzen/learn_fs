# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/ogg_mapping.c

## Role

`ogg_mapping.c` defines the constants for the Ogg FLAC mapping shared by encoder and decoder aspect code.

## Contents

It exports:

- `FLAC__OGG_MAPPING_PACKET_TYPE_LEN = 8`
- `FLAC__OGG_MAPPING_FIRST_HEADER_PACKET_TYPE = 0x7f`
- `FLAC__OGG_MAPPING_MAGIC = "FLAC"`
- `FLAC__OGG_MAPPING_VERSION_MAJOR_LEN = 8`
- `FLAC__OGG_MAPPING_VERSION_MINOR_LEN = 8`
- `FLAC__OGG_MAPPING_NUM_HEADERS_LEN = 16`

The byte-length macros live in the paired header.

## Risks / Edge Cases

The mapping constants must stay consistent with `private/ogg_mapping.h` and with the Ogg FLAC specification. Encoder/decoder aspect code relies on these values to build and strip the first header packet.

## Dependencies

Includes only `private/ogg_mapping.h`.
