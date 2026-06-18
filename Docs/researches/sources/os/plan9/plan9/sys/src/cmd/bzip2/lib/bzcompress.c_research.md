# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzcompress.c

Core streaming compression state machine for libbzip2.

Provides:

- `BZ2_bzCompressInit()`: validates config, installs allocators, allocates `EState`, block arrays, and frequency table.
- Run-length input staging via `init_RL`, `add_pair_to_block`, `flush_RL`, and `ADD_CHAR_TO_BLOCK`.
- `copy_input_until_stop()` and `copy_output_until_stop()` for incremental stream progress.
- `handle_compress()` to transition between input and output states.
- `BZ2_bzCompress()`: implements `BZ_RUN`, `BZ_FLUSH`, and `BZ_FINISH` sequencing.
- `BZ2_bzCompressEnd()`: frees allocated compression state.

It writes full compressed blocks through `BZ2_compressBlock()` and tracks total input/output counters, flush expectations, finish expectations, block CRCs, and run-length encoding before block sorting.
