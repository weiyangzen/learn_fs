# sources/security-integrity/selinux/libselinux/fuzz/selabel_file_text-fuzzer.c

## Purpose
This libFuzzer harness exercises textual file-context parsing and lookup in libselinux. It converts fuzzer bytes into a text file-context definition and lookup key, then drives internal label-file parsing and matching.

## Important APIs, types, and functions
`LLVMFuzzerTestOneInput()` is the fuzz entry point. Helpers `null_log()`, `validate_context()`, `write_full()`, and `convert_data()` support callback behavior and in-memory file conversion. The harness uses `process_text_file()`, `sort_specs()`, `cmp()`, `lookup_all()`, `free_lookup_result()`, and `free_spec_node()` from `../src/label_file.h`. Control bits select partial lookup, find-all behavior, and optional `S_IFSOCK` mode.

## Control flow
The first byte is a constrained control byte. The remaining input is split at the first `0xde 0xad 0xbe 0xef` separator into file-context text and a NUL-terminated lookup key. The text is written to a memfd-backed `FILE *`, parsed into a mocked `selabel_handle`, sorted, self-compared, and queried. Successful lookup results are validated for nonempty regex/context, no translated context, prior validation, and sane prefix length.

## State and persistence behavior
The harness uses only heap allocations, an anonymous memfd, mmap areas created by parser internals, and global SELinux callbacks. It frees all owned state on cleanup and creates no filesystem artifacts.

## Dependencies and integration points
It depends on libFuzzer, Linux/GNU interfaces, public `selinux/label.h`, private label-file parser internals, and SELinux callback APIs. It complements the compiled-context harness by targeting the text parser path.

## Risks and edge cases
The target is Linux-specific because of `memfd_create()`. Assertions double as correctness checks and require assert-enabled builds. The simplistic separator format means some fuzz bytes are discarded before parser entry if the separator is absent or first. Global callbacks can affect other code in the same process.

## Test signals
Useful seeds include minimal valid file-context lines, regex-heavy paths, invalid contexts, empty contexts, `<<none>>`, malformed line formats, comments/whitespace, mode-qualified entries, very long regexes, partial-match paths, and keys containing embedded unusual bytes before NUL termination.
