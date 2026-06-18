# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/stream_decoder.h

Public libFLAC stream decoder API header for native FLAC and optional Ogg FLAC decoding.

Important contents:
- Includes `stdio.h` for `FILE`, plus `export.h` and `format.h`.
- Documents the decoder lifecycle: create with `FLAC__stream_decoder_new()`, configure with setters, initialize via stream/FILE/filename APIs, process data, finish/reset/flush, and delete.
- Defines decoder state enum values from metadata search through frame reading, end-of-stream, Ogg error, seek error, abort, allocation failure, and uninitialized state.
- Defines init status enum values for success, unsupported container, invalid callbacks, allocation failure, file-open failure, and already-initialized use.
- Defines callback status enums for read, seek, tell, length, write, and error callbacks, each with exported string tables.
- Defines opaque `FLAC__StreamDecoder` with protected/private implementation pointers.
- Declares callback typedefs for read, seek, tell, length, EOF, write decoded PCM, metadata, and error reporting.
- Declares constructor/destructor, configuration setters for Ogg serial number, MD5 checking, metadata response/ignore filters, and APPLICATION-specific metadata filters.
- Declares query functions for decoder state, resolved state string, MD5 setting, total samples, channels, channel assignment, bits per sample, sample rate, blocksize, decode byte position, and client data.
- Declares native and Ogg initialization variants for caller-supplied callbacks, open `FILE *`, and filenames.
- Declares processing/control functions: `finish`, `flush`, `reset`, `process_single`, `process_until_end_of_metadata`, `process_until_end_of_stream`, `skip_single_frame`, and sample-accurate `seek_absolute`.

Implementation notes:
- This is a public declaration header, not the decoder implementation.
- The callback API separates input transport from decoded output. Clients supply encoded bytes through read callbacks and receive decoded channel buffers through the write callback.
- Seeking requires a compatible set of seek, tell, length, and EOF callbacks; otherwise seeking is unsupported.
- FILE-based initialization transfers ownership of the supplied `FILE *` to the decoder, except for `stdin`; filename-based initialization uses `fopen()` semantics and allows `NULL` for stdin.
- Metadata callbacks receive temporary objects that must not be modified and do not live beyond the callback; clients needing persistence must clone them.
- MD5 checking is optional and is disabled automatically when no STREAMINFO signature exists or when seeking is attempted.
- Setter functions are only valid while the decoder is uninitialized.

Filesystem relevance:
- No filesystem implementation is present. The only file-facing behavior is decoder input initialization from filenames or `FILE *`, plus seek/tell/length callback contracts. Within 9front, this supports audio decoding in the vendored libFLAC library.
