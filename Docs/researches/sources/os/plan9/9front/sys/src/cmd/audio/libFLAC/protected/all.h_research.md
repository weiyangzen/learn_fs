# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/protected/all.h

## Role

`protected/all.h` is an umbrella include for protected stream decoder and encoder state headers.

## Contents

It includes `stream_decoder.h` and `stream_encoder.h`.

## Risks / Edge Cases

This header exposes protected internals to source files that need access to libFLAC object state beyond the public API. It increases coupling to internal structure layouts.

## Dependencies

Depends on the protected decoder and encoder headers.
