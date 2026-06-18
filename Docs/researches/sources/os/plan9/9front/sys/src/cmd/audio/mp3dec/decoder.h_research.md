# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/decoder.h

This header defines the public decoder control API. It declares `enum mad_decoder_mode` for sync/async operation, `enum mad_flow` for callback control (`CONTINUE`, `STOP`, `BREAK`, `IGNORE`), and `struct mad_decoder`, which stores options, async pipe/process metadata, synchronous decode state, callback data, and callback function pointers.

The callback surface is the key contract: clients provide input data, may inspect headers, may filter decoded frames, consume PCM, handle errors, and optionally exchange messages with an async decoder. `mad_decoder_options` is a macro that writes option flags into the decoder before running.

Within this group, `main.c` uses this API as a small MP3 player: input reads stdin, header handles seeking, output writes converted PCM, and error skips tags/reports decode errors. This header depends on `stream.h`, `frame.h`, and `synth.h` because the callback signatures expose those structures.
