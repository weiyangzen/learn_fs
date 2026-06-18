# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/decoder.c

This file implements libmad's callback-driven decoder orchestration. `mad_decoder_init` records client callbacks for input, header, filter, output, error, and message handling. `mad_decoder_run` allocates the synchronous state bundle (`mad_stream`, `mad_frame`, `mad_synth`) and dispatches to synchronous decoding, or to an optional asynchronous mode when `USE_ASYNC` is compiled in.

The synchronous loop repeatedly asks the input callback for data, decodes headers and frames, runs an optional filter, synthesizes PCM via `mad_synth_frame`, and delivers PCM to the output callback. Recoverable errors are routed through either a user callback or `error_default`, which ignores CRC errors and mutes repeated bad CRC frames. Nonrecoverable errors break the loop.

The async path, guarded by `USE_ASYNC`, uses pipes, `fork`, and simple length-prefixed messages between parent and child. In this 9front player, `main.c` runs only `MAD_DECODER_MODE_SYNC`, so the active path is the callback loop around `stream.c`, `frame.c`, layer decoders, and synthesis.
