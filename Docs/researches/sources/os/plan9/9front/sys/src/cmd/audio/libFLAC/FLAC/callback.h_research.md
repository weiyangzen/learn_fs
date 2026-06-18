# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/callback.h

Public libFLAC I/O callback type definitions.

Important contents:
- Defines opaque `FLAC__IOHandle`.
- Defines read, write, seek, tell, EOF, and close callback signatures.
- Defines `FLAC__IOCallbacks`, bundling those callback pointers.
- Documents 64-bit offset expectations for seek/tell callbacks.

Used by metadata and stream interfaces needing caller-supplied I/O.
