# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/VbrTag.h

This header declares the Xing VBR tag interface and parsed-tag structure.

Key definitions:
- Xing flag bits: `FRAMES_FLAG`, `BYTES_FLAG`, `TOC_FLAG`, and `VBR_SCALE_FLAG`.
- `NUMTOCENTRIES`: 100.
- `FRAMES_AND_BYTES`: convenience mask.
- `VBRTAGDATA`: parsed VBR header fields including MPEG id, samplerate, flags, frame count, byte count, VBR scale, TOC, and header size.

Exported functions:
- `CheckVbrTag()`
- `GetVbrTag()`
- `SeekPoint()`
- `InitVbrTag()`
- `PutVbrTag()`
- `AddVbrFrame()`

Dependencies and integration:
- Includes `lame.h`.
- Implemented primarily by `VbrTag.c`.
- Used by encoder initialization/finalization and possibly MP3 input parsing.

Risks and edge cases:
- The comment says `toc` may be `NULL`, but the struct contains an inline array, not a pointer; that comment appears stale.
- `SeekPoint()` is declared here but not implemented in the paired file read in this group.
