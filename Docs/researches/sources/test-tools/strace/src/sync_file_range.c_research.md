# sources/test-tools/strace/src/sync_file_range.c

Purpose: decoder for the standard argument order of `sync_file_range`.

Important APIs/types/functions: `SYS_FUNC(sync_file_range)`, `printfd`, `print_arg_lld`, and `sync_file_range_flags`.

Control flow: prints fd, decodes 64-bit `offset` and `nbytes` using `print_arg_lld` because ABI argument slots may vary, then prints flag names.

State and persistence behavior: stateless decoder.

Dependencies and integration points: depends on large-argument helpers in `defs.h`, `<linux/fs.h>`, and generated flag xlats.

Risks: correctness depends on `print_arg_lld` advancing the argument index for architectures that split 64-bit arguments.

Test signals: native and compat ABIs, negative-looking large offsets, zero bytes, all named flags, and unknown flag bits.
