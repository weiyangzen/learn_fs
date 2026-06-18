# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/get_audio.h

This header declares audio input helpers and fallback audio container structures.

Key definitions:
- `sound_file_format`: enum for unknown, raw, WAVE, AIFF, MPEG Layer I/II/III, and Ogg.
- `blockAlign`: AIFF sound-data offset/block-size pair.
- `IFF_AIFF`: fallback AIFF metadata structure.

Exports:
- `init_outfile()`
- `init_infile()`
- `close_infile()`
- `get_audio()`
- `lame_decoder()`
- `SwapBytesInWords()`

Conditional declarations:
- If `LIBSNDFILE` is enabled, includes `sndfile.h`.
- Otherwise includes `portableio.h` and declares older AIFF/WAV helper prototypes.

Integration:
- Used by command-line encode/decode front ends.
- Implemented by `get_audio.c`.

Risks:
- Header exposes legacy fallback prototypes that are not all implemented in `get_audio.c`, suggesting compatibility remnants.
- API relies on global state configured outside the header.
