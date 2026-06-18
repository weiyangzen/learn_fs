# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jerror_.h

## Identity

- Lines/bytes: 29 lines, 903 bytes.
- SHA-256: `40bc4f4073f2f63b9fc7e2b2dc477cdad06b85dee462f452d6ba7a29a17b4ec8`.
- Role: Ghostscript wrapper for IJG `jerror.h`.

## Contents

The file has a single include guard, `jerror__INCLUDED`, and chooses between:

- `<jerror.h>` when `SHARE_JPEG` is true.
- `"jerror.h"` when Ghostscript builds or uses its private JPEG headers.

## Dependencies

- Depends on build-time macro `SHARE_JPEG`.
- External/shared mode requires system JPEG headers.
- Private mode requires local IJG `jerror.h`.

## Behavior And Integration

This wrapper allows Ghostscript code to include a stable wrapper name while switching between shared-system JPEG and bundled JPEG builds.

## Research Notes

- No algorithms or state are defined here.
- Its main significance is build isolation and avoiding ambiguous header selection.
