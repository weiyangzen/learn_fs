# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/get_audio.c

This file implements input audio opening, decoding, PCM reading, simple decoding-to-WAV, and fallback WAV/AIFF/raw parsers for the LAME-derived command.

Key responsibilities:
- Opens input and output files.
- Reads PCM, MP3, or Ogg samples into encoder frame buffers.
- Converts interleaved PCM into left/right channel arrays.
- Handles byte swapping and 8-bit-to-16-bit sample expansion.
- Writes simple WAV headers for decode mode.
- Supports libsndfile-based input when `LIBSNDFILE` is enabled.
- Provides fallback WAV/AIFF/raw header parsing when libsndfile is unavailable.
- Provides mpglib-based MP3 header probing and frame decoding when `HAVE_MPGLIB` is enabled.

Important globals:
- `count_samples_carefully`
- `pcmbitwidth`
- `mp3input_data`
- `num_samples_read`
- `musicin`

Important functions:
- `fskip()`: forward skip helper that falls back to read/discard for pipes.
- `init_outfile()`: opens stdout or binary output file.
- `init_infile()` / `close_infile()`: manage global input file.
- `SwapBytesInWords()`: byte-swaps 16-bit samples, optimized for 32- or 64-bit unsigned long.
- `get_audio()`: reads one encoder frame's worth of samples into `[2][1152]`.
- `read_samples_ogg()` and `read_samples_mp3()`: decode compressed input through optional decoders.
- `WriteWaveHeader()`: writes a PCM WAV header.
- `lame_decoder()`: simple decode loop from compressed/raw input to WAV PCM output.
- `OpenSndFile()` / `CloseSndFile()`: format-specific open/close.
- Fallback-only `parse_wave_header()`, `parse_aiff_header()`, `parse_file_header()`.
- mpglib-only `lame_decode_initfile()` and `lame_decode_fromfile()`.

Dependencies and integration:
- Includes `lame.h`, `main.h`, `get_audio.h`, `portableio.h`, `timestatus.h`, and `lametime.h`.
- Optional dependencies: libsndfile, mpglib, Vorbis.
- Uses global command-line state such as `input_format`, `swapbytes`, and `silent`.
- The encoder front end calls `init_infile()`, repeatedly calls `get_audio()`, then `close_infile()`.

Control flow:
- `get_audio()` determines how many samples to read, optionally clamps to known sample count, dispatches by `input_format`, and returns samples per channel.
- PCM default path reads interleaved samples and deinterleaves mono/stereo into the two-channel output buffer.
- Compressed paths call decoder wrappers and verify channel count and samplerate have not changed.
- Decode mode writes WAV data while skipping known decoder/encoder delay for MPEG formats.

Fallback parser behavior:
- WAV parsing looks for `RIFF`, `WAVE`, `fmt `, and `data` chunks, supports PCM only, and sets channels, samplerate, bit width, and sample count.
- AIFF parsing looks for `FORM`, `AIFF`, `COMM`, and `SSND`, validates PCM-like constraints, and sets corresponding LAME fields.
- Raw fallback rewinds to byte zero if header detection fails.

Risks and edge cases:
- Uses process-global input state, so it is not reentrant.
- Many fatal input errors call `exit()`, which is command-line friendly but not library friendly.
- Some format strings use `%ud` for channel values, which is suspicious C formatting.
- mpglib decode reads fixed 100-byte chunks and treats short reads as errors/end.
- `fskip()` prints directly to stderr on unsupported seek cases.
- No direct filesystem implementation logic; file I/O is ordinary audio command input/output.
