# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfbcp.c

Implements BCP and TBCP filter creation operators.

Key behavior:
- Defines `BCPEncode`, `BCPDecode`, `TBCPEncode`, and `TBCPDecode`.
- Encode operators use simple write-filter wrappers.
- Decode operators initialize `stream_BCPD_state` with no-op handlers for BCP out-of-band interrupt/status signals.
- Supports both ordinary Binary Communications Protocol and Tagged BCP templates.

Dependencies:
- Uses stream templates from `sbcp.h` and Ghostscript filter helpers.

Research notes:
- This file deliberately ignores BCP signal callbacks, making the filters pure byte-stream transforms from the interpreter’s point of view.
