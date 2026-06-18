# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/ogg_mapping.h

## Role

`private/ogg_mapping.h` declares constants and byte-length macros for the Ogg FLAC mapping header.

## Contents

It defines byte lengths for packet type, mapping magic, version major/minor, and number-of-header-packets fields. It declares bit-length constants, first header packet type, and mapping magic defined in `ogg_mapping.c`.

## Important Details

Encoder code uses these constants to construct the synthetic first Ogg FLAC packet. Decoder code uses the same constants to validate and strip the Ogg mapping prefix before handing native FLAC bytes to the decoder.

## Dependencies

Includes `FLAC/ordinals.h`.
