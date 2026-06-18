<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-success-v.c -->
## sources/test-tools/strace/tests/bpf-success-v.c

Purpose: Verbose injected-success variant of the BPF syscall decoder test.

Important APIs/types/functions: Defines `INJECT_RETVAL 42` and includes `bpf-v.c`, which defines `VERBOSE 1` before including `bpf.c`.

Control flow: Runs the full BPF command matrix with verbose nested data printing and injected successful return formatting.

State and persistence: Inherits `bpf.c` allocations; injection prevents reliance on actual kernel success.

Dependencies and integration: Combines verbose BPF attr decoding with success-path return handling.

Risks: Very large expected output; changes to verbose printers or xlat tables can affect many lines.

Test signals: Output should include expanded extra-data blobs, arrays, strings, flags, and ` (INJECTED)` return annotations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-success-v.c -->
