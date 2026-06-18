# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/gcov.h

Imported Xen public coverage-data ABI.

Purpose:
- Defines Xen’s exported coverage blob tags and structures, distinct from GCC’s native gcov layout.

Key content:
- Defines coverage tag base, file/function/counter/end tags, counter count, and helper macros for counter tag recognition.
- Documents blob grammar: file records, counter records, function records, and terminator.
- Defines variable-length `xencov_file`, `xencov_counter`, `xencov_function`, `xencov_functions`, and `xencov_end`.

Integration:
- Not used by the 9front guest runtime.
- Vendored for Xen tooling/control completeness.

Risks/notes:
- Variable-length structure parsing requires respecting 8-byte alignment and tag ordering.
