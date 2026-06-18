# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/stream.c

Implements Ghostscript’s generic stream package core.

Key behavior:
- Defines GC descriptors and relocation for `stream`, including buffer/string pointers, filter links, interpreter file-list links, state, and file name.
- Finalizer closes only valid non-temporary file streams to avoid freeing non-file stream storage during GC finalization.
- Implements allocation and initialization:
  - `s_init`
  - `s_alloc`
  - `s_init_state`
  - `s_alloc_state`
  - `s_std_init`
- Manages stream file names with copied, null-terminated storage through `ssetfilename` and `sfilename`.
- Provides standard no-op/reset/flush/close/switch helpers.
- `s_disable` invalidates a stream, clears GC-visible links, resets state, and frees the copied filename.
- Implements filter flushing/closing, including `CloseTarget` propagation via `close_strm`.
- Provides generic API functions: `savailable`, `stell`, `spseek`, `sswitch`, `sclose`, `spgetcc`, `spputc`, `sungetc`, `sgets`, `sputs`, `spskip`, and `sreadline`.
- `spgetcc` preserves filter read-ahead by honoring `min_left` and can close at EOD.
- `sgets` can bypass the stream buffer for large reads when template guarantees permit.
- `sreadline` handles CR/LF variants, optional prompts, fixed or growable buffers, and stdin-specific EOL behavior.
- `sreadbuf` and `swritebuf` traverse filter pipelines by temporarily reversing `strm` links, updating `end_status` while unwinding.
- `stream_compact` moves unread data to the bottom of the buffer and advances logical position.
- Implements string read/write streams, reusable string streams, and a position-only write stream.
- Implements filter construction and teardown:
  - `s_init_filter`
  - `s_add_filter`
  - `s_close_filters`
- Defines NullEncode/NullDecode templates using `stream_move`.

Dependencies and interactions:
- Includes `stdio_.h`, `memory_.h`, `gdebug.h`, `gpcheck.h`, `stream.h`, and `strimpl.h`.
- File stream constructors declared in `stream.h` are implemented elsewhere (`sfxstdio.c`/`sfxfd.c`), not in this file.
- Used by interpreter filters, file objects, image data sources, compression filters, and output devices.

Research relevance:
- Core buffering and filter-pipeline engine. Correct EOD/read-ahead behavior here affects all PostScript/PDF stream consumers.
