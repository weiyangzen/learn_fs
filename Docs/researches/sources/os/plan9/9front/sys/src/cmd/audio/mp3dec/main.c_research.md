# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/main.c

This file is the Plan 9 command frontend: a simple MP3 player derived from libmad's `minimad.c`. It reads compressed MP3 data from standard input, decodes it synchronously with libmad callbacks, and writes fixed-point PCM samples to `/bin/audio/pcmconv` for conversion/playback.

The `input` callback preserves leftover bytes from `stream->next_frame`, reads more stdin data into a static 32 KiB buffer, updates `offset`, and calls `mad_stream_buffer`. The `header` callback implements `-s` seeking by counting decoded sample positions and ignoring frames until the target time is reached. The `output` callback starts or restarts `pcmconv` when sample rate/channel count changes, formats samples as signed fixed-point interleaved little-endian-ish bytes, clips to `[-MAD_F_ONE, MAD_F_ONE)`, and writes to the converter pipe.

The `error` callback skips ID3v1 `TAG` and ID3v2 `ID3` metadata on lost sync and optionally logs decode errors with `-d`. `main` parses `-d` and `-s`, initializes callbacks, runs sync decode, waits for `pcmconv`, and exits.
