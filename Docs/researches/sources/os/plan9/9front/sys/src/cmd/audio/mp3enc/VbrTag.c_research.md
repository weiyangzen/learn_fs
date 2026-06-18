# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/VbrTag.c

This file implements Xing-style VBR tagging for the LAME-derived MP3 encoder.

Key responsibilities:
- Maintains a compressed seek table as frames are encoded.
- Detects and parses existing Xing VBR headers.
- Reserves a dummy first MP3 frame for the eventual VBR header.
- Rewrites that reserved frame at the end with final frame count, byte count, TOC, quality scale, and LAME version string.
- Handles ID3v2-at-start offset when rewriting the VBR tag.

Important functions:
- `addVbr(VBR_seek_info_t *v, int bitrate)`: accumulates bitrate samples into a bounded bag, thinning entries when full.
- `Xing_seek_table(...)`: converts the accumulated bag into 100 TOC seek entries.
- `AddVbrFrame(lame_global_flags *gfp)`: initializes and updates `gfc->VBR_seek_table`, increments `nVbrNumFrames`.
- `CreateI4(...)` and `ExtractI4(...)`: big-endian 32-bit encoding/decoding helpers.
- `CheckVbrTag(unsigned char *buf)`: checks only for Xing marker at the MPEG-header-derived offset.
- `GetVbrTag(VBRTAGDATA *pTagData, unsigned char *buf)`: parses Xing flags, frames, bytes, TOC, VBR scale, samplerate, and header size.
- `InitVbrTag(lame_global_flags *gfp)`: reserves a dummy header frame by writing dummy bytes into the bitstream.
- `PutVbrTag(lame_global_flags *gfp, FILE *fpStream, int nVbrScale)`: seeks back and writes final VBR header bytes.

Dependencies and integration:
- Includes `machine.h`, `VbrTag.h`, `version.h`, and `bitstream.h`.
- Uses `bitrate_table`, `samplerate_table`, and `BitrateIndex()`.
- Uses `add_dummy_byte()` to reserve bytes in the encoder bitstream.
- `lame.c` calls `InitVbrTag()` during initialization, `AddVbrFrame()` after frames, and `PutVbrTag()` through `lame_mp3_tags_fid()`.

Data flow:
- During encoding, frame bitrates are recorded in `gfc->VBR_seek_table`.
- At finalization, the output file is inspected for an optional ID3v2 tag, the first real frame's MPEG header fields are used as a template, and a Xing frame is written at the correct offset.
- The TOC entries approximate byte positions as `toc[i] / 256 * total_bytes`.

Risks and edge cases:
- `AddVbrFrame()` allocates a 400-entry seek bag and reports failure but otherwise leaves VBR tagging degraded.
- `PutVbrTag()` requires a seekable `FILE *`; it returns `-1` when the file is empty or no VBR frames were recorded.
- Several `fread()` and `fseek()` calls are not strongly checked.
- `assert()` checks enforce header frame sizing; disabled assertions could hide bad sizing assumptions.
- `VbrTag.h` declares `SeekPoint()`, but this file does not define it.
