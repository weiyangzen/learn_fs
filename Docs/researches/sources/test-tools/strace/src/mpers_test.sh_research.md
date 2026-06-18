<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mpers_test.sh -->
# sources/test-tools/strace/src/mpers_test.sh

Purpose: self-test for mpers generation using a synthetic structure with padding, arrays, unions, pointers, and integer widths.
Important APIs/types/functions: creates `sample.c`, `sample.expected`, invokes `mpers.sh`, and compares generated `sample_struct.h` with `cmp`.
Control flow: derives pointer size from the mpers name, writes fixture source/expected output, sets CPP/CFLAGS including `IN_MPERS`, runs generation, and fails on mismatch.
State and persistence behavior: creates a `mpers-$mpers_name` test directory. Dependencies and integration points: validates `mpers.awk`, `mpers.sh`, and `mpers_type.h` behavior.
Risks: expected fixture must track generator output exactly; compiler layout changes can expose bugs. Test signals: this script is itself the primary test and should be run for m32/mx32-like names.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mpers_test.sh -->
