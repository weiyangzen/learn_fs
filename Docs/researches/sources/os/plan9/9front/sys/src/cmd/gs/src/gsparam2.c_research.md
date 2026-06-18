# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparam2.c

Implements a stream-oriented serializer/unserializer for `gs_param_list`, described as a redesigned future interface in `gsparams.h`.

Main behavior:
- `gs_param_list_puts` enumerates keys from a READ-mode list and writes compressed key lengths, types, keys, values, arrays, string arrays, and nested collections to a `stream`.
- `gs_param_list_gets` reads that stream format into a WRITE-mode parameter list, allocating aggregate data with the provided memory allocator.
- `sput_word`/`sget_word` encode variable-length 7-bit chunks.
- `sput_bytes`/`sget_bytes` bridge to Ghostscript stream byte APIs.

Important caveat:
- `gsparams.h` has this interface inside the disabled `#if 0` branch, so this file may not be part of the active build path.
- The local `sget_bytes` function has an apparent stray `};` before `return 0`, which would be syntactically invalid if compiled as shown.
