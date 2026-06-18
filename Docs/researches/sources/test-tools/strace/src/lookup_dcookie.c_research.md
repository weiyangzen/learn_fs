<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/lookup_dcookie.c -->
# sources/test-tools/strace/src/lookup_dcookie.c

Purpose: decodes `lookup_dcookie`, which maps a kernel dcookie to a path buffer.
Important APIs/types/functions: `SYS_FUNC(lookup_dcookie)`, `printbigval`, `printpathn`, and buffer length/return-value handling.
Control flow: prints the 64-bit cookie on entry; on exit prints either the returned path limited by `u_rval` or the raw buffer address on error, then prints buffer length.
State and persistence behavior: stateless. Dependencies and integration points: syscall table entry and path-printing helpers.
Risks: path length must be bounded by the actual return value to avoid over-reading. Test signals: success, error, and truncated-buffer lookup_dcookie traces.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/lookup_dcookie.c -->
