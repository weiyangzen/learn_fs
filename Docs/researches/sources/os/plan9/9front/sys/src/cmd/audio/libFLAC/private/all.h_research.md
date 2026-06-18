# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/all.h

## Role

`private/all.h` is an umbrella include for libFLAC private headers. It aggregates internal declarations for bit I/O, CPU detection, CRC, predictors, floating/fixed-point support, metadata, memory, and encoder framing.

## Contents

It includes `bitmath.h`, `bitreader.h`, `bitwriter.h`, `cpu.h`, `crc.h`, `fixed.h`, `float.h`, `format.h`, `lpc.h`, `md5.h`, `memory.h`, `metadata.h`, and `stream_encoder_framing.h`.

## Risks / Edge Cases

As an umbrella header, it increases compile-time coupling. Any header added here becomes broadly visible to private implementation files that include `private/all.h`.

## Dependencies

Depends on all listed private headers and their transitive public FLAC/share headers.
