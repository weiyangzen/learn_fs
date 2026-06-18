# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/vorbis/vorbisfile.h

Public libvorbisfile convenience API header for stdio/callback-based Ogg Vorbis opening, seeking, and decoding.

Important contents:
- Defines `ov_callbacks` with read, seek, close, and tell function pointers.
- Provides static callback presets unless `OV_EXCLUDE_STATIC_CALLBACKS` is defined:
  - `OV_CALLBACKS_DEFAULT`
  - `OV_CALLBACKS_NOCLOSE`
  - `OV_CALLBACKS_STREAMONLY`
  - `OV_CALLBACKS_STREAMONLY_NOCLOSE`
- Defines ready-state constants `NOTOPEN`, `PARTOPEN`, `OPENED`, `STREAMSET`, and `INITSET`.
- Defines `OggVorbis_File`, holding datasource, seek/index metadata, Ogg sync/stream state, Vorbis info/comment arrays, decode state, tracking counters, and callbacks.
- Declares open/test/clear, bitrate/stream info, raw/PCM/time seeking and telling, info/comment access, float/integer read APIs, crosslap, and half-rate APIs.

Integration points:
- Includes `<stdio.h>` and `codec.h`.
- Wraps Ogg container state plus Vorbis decoder state.
- Callback design allows stdio or custom data sources.

Risk and review signals:
- Static callback objects in a header intentionally create one copy per including translation unit.
- `_ov_header_fseek_wrap()` has platform-specific large-file seek handling.
- `OggVorbis_File` is public ABI and includes overloaded `pcmlengths` for binary compatibility.
- Callback implementations must return stdio-compatible values, especially `-1` for unseekable seek callbacks.

Filesystem relevance:
- Filesystem-adjacent only as an audio file convenience API: it opens/seeks/reads streams through stdio or callbacks, but it is not filesystem implementation code.
