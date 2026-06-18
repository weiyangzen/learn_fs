# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gx.h

Purpose: Common internal Ghostscript include wrapper.

Contents:
- Includes core internal headers: `stdio_.h`, `gserror.h`, `gsio.h`, `gstypes.h`, `gsmemory.h`, and `gdebug.h`.
- Forward-declares opaque `gs_imager_state` and `gs_state`.

Behavior:
- Centralizes pervasive internal definitions so lower-level files can include one stable core header.
- Avoids exposing graphics-state structure definitions at this level.

Dependencies:
- Pulls in broad Ghostscript base types and debug/error/memory APIs.

Notable risks:
- Because widely included, any changes here have large compile-time impact.
