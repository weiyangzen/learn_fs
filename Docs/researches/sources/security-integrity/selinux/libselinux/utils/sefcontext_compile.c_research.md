<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/sefcontext_compile.c -->
# sources/security-integrity/selinux/libselinux/utils/sefcontext_compile.c

## Purpose
Compiles text `file_contexts` specifications into the binary mmap-able format consumed by libselinux file labeling.

## Important APIs, Types, And Functions
`process_file()` feeds lines to `process_line()`. `create_sidtab()` deduplicates raw contexts. `write_sidtab()`, `write_literal_spec()`, `write_regex_spec()`, `write_spec_node()`, and `write_binary_file()` serialize the binary format. `main()` handles `-o`, `-p`, `-r`, `-i`, and `-V`.

## Control Flow
The tool optionally loads a binary policy for validation, constructs a dummy file-label handle and saved data tree, parses the text file, sorts specs, creates a SID table, writes to a mode-preserving temporary file with `mkstemp()`, then atomically renames it to the output.

## State And Persistence Behavior
Writes a compiled `.bin` file containing magic/version, regex backend metadata, context table, and spec tree. Temporary files are unlinked on failure.

## Dependencies And Integration Points
Uses libsepol validation, internal label-file structures, sidtab, regex serialization, endian conversion, and file-label parser internals.

## Risks And Test Signals
Risks include binary format compatibility, regex portability, context validation callback behavior, temp-file cleanup, length overflows, and partial writes. Tests should cover default output, `-o`, `-p` valid/invalid policy, `-r`, `-i`, `-V`, malformed specs, long strings, atomic rename, and compiled-file load by `selabel_open()`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/sefcontext_compile.c -->
