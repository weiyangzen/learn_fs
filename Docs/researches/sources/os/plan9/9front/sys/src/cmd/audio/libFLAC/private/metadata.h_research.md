# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/metadata.h

## Role

`private/metadata.h` exposes internal metadata cleanup helpers that are not part of the normal public API.

## API Surface

It declares:

- `FLAC__metadata_object_delete_data()`
- `FLAC__metadata_object_cuesheet_track_delete_data()`

These free malloc-owned data inside metadata objects or cue sheet tracks without necessarily returning the object to the exact state created by public constructors.

## Risks / Edge Cases

The warning is important: after deleting embedded data, the containing object may be inconsistent for normal public use unless the caller reinitializes fields. This is a low-level cleanup primitive.

## Dependencies

Includes public `FLAC/metadata.h`.
