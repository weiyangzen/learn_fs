# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/export.h

Public libFLAC export/version header.

Important contents:
- Defines `FLAC_API` for Windows DLL import/export, visibility attributes, or empty default.
- Defines libFLAC API version constants.
- Declares `FLAC_API_SUPPORTS_OGG_FLAC`.

This isolates platform symbol-export mechanics for public libFLAC headers.
