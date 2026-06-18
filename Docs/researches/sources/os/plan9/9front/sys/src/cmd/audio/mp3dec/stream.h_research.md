# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/stream.h

This header defines the stream-level input and error model. Constants include `MAD_BUFFER_GUARD` for safe bit reads past frame data and `MAD_BUFFER_MDLEN` for the Layer III main-data reservoir size. `enum mad_error` classifies buffer, allocation, sync/header, CRC, Layer I/II, and Layer III decode failures; `MAD_RECOVERABLE` treats errors with high-byte category bits as recoverable.

`struct mad_stream` tracks caller-provided input buffer bounds, deferred skip length, sync state, inferred free bitrate, current/next frame pointers, primary bit pointer, ancillary-data pointer/length, Layer III reservoir buffer/length, decode options, and current error code. Options include ignoring CRC and half-sample-rate generation, with some channel-selection options disabled.

The public functions initialize/finish a stream, set a buffer, request a skip, search for sync, and stringify errors. This structure is shared across the full decoder pipeline and is mutated by input callbacks, frame parsing, layer decoders, and error handlers.
