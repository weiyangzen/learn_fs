# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sarc4.h

Declares Arcfour stream cipher state, key setup, stream template, and buffer helper. The state embeds stream common fields plus RC4 indices `x`/`y` and a 256-byte permutation table.

Dependencies are `scommon.h` and `strimpl.h` for template use. The header frames the algorithm as functionally equivalent to PDF-specified RC4 while avoiding the trademarked name in code comments.

This is PDF encryption filter support, not filesystem infrastructure.
