# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/vorbis/codec.h

Public libvorbis codec API header adapted for 9front.

Important contents:
- Contains Plan 9 pragma: `#pragma lib "/sys/src/cmd/audio/libvorbis/libvorbis.a$O"`.
- Defines public structs:
  - `vorbis_info`
  - `vorbis_dsp_state`
  - `vorbis_block`
  - `alloc_chain`
  - `vorbis_comment`
- Declares general info/comment/block/DSP lifecycle APIs.
- Declares analysis/encoding packet APIs.
- Declares synthesis/decoding APIs.
- Declares half-rate decode APIs.
- Defines Vorbis error codes such as `OV_EOF`, `OV_HOLE`, `OV_EBADHEADER`, `OV_ENOTAUDIO`, and `OV_EBADPACKET`.

Integration points:
- Included by nearly all libvorbis source files and public consumers.
- Depends on `<ogg/ogg.h>`.
- `codec_setup` and `backend_state` are opaque public pointers to private internal structures.

Risk and review signals:
- This is public API/ABI surface; struct layout changes affect applications.
- Comment query APIs return owned internal pointers.
- Error code values are API-visible compatibility constants.
- Plan 9 pragma is local build integration.

Filesystem relevance:
- No filesystem logic. It is codec public API declaration.
