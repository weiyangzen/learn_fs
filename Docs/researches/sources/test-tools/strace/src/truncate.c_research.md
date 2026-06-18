# sources/test-tools/strace/src/truncate.c

Purpose: decoders for `truncate`, `truncate64`, `ftruncate`, and `ftruncate64`.

Important APIs/types/functions: four `SYS_FUNC` implementations, `printpath`, `printfd`, `PRINT_VAL_U`, and `print_arg_llu`.

Control flow: path-based calls print path then length; fd-based calls print fd then length. 64-bit variants use `print_arg_llu` to account for ABI argument splitting.

State and persistence behavior: stateless; may read path string from tracee memory.

Dependencies and integration points: selected by syscall tables for file truncation calls.

Risks: non-64 variants print length as unsigned long argument; 64-bit variants rely on correct ABI index handling.

Test signals: valid/bad paths, decoded fd paths with `-y`, zero length, large 64-bit length, and compat ABI argument splitting.
