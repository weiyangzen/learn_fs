# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/vorbis_interface.c

Optional LAME bridge to libvorbis for Ogg Vorbis decoding and encoding, compiled only under `HAVE_VORBIS`.

Key responsibilities:
- Initializes Ogg/Vorbis decode state from an input file, validates the first Vorbis header, reads comment/codebook headers, and exposes stream metadata through `mp3data_struct`.
- Decodes Vorbis packets to signed 16-bit PCM arrays in chunks.
- Initializes Vorbis encoding mode based on LAME compression ratio and channel/sample-rate settings.
- Emits Vorbis headers, encodes LAME frame-sized PCM buffers, flushes pages into caller-provided output buffers, and finishes/cleans the stream.
- Adds a basic Vorbis comment identifying the LAME libvorbis interface.

Dependencies:
- Uses libogg/libvorbis headers and older mode presets from `modes/modes.h`.
- Uses LAME diagnostics through `ERRORF`/`MSGF`.

Research notes:
- Decode and encode state is stored in file-scope globals, so this interface is not reentrant.
- Output buffer overflow returns negative error codes.
- Some ID3-to-Vorbis comment mapping code is disabled by a compile-time guard.
