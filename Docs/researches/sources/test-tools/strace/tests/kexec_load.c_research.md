<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kexec_load.c -->
# sources/test-tools/strace/tests/kexec_load.c

Purpose: Tests decoding of the older `kexec_load` syscall, especially segment-array truncation and architecture/operation flags.

Important APIs/types/functions: Uses `syscall(__NR_kexec_load)`, local `struct segm`, `tail_alloc`, `fill_memory`, and `struct strval` flag fixtures.

Control flow: Allocates seventeen segment descriptors, fills them with deterministic data, then issues calls for NULL/zero arguments, bogus segment pointers, full arrays, arrays that should be truncated with ellipsis, tail subarrays, and multiple flag combinations.

State/persistence behavior: Bogus entry points, segment pointers, and missing privilege keep the syscall from loading a kernel. Only local memory is modified.

Dependencies: Requires syscall number availability, pointer-size conditionals, and kexec flag constants in strace expectations.

Integration points: Validates array-of-struct decoding, ellipsis and fault-pointer annotations, kexec architecture flag printing, and scalar argument formatting.

Risks: Segment count truncation rules are easy to regress. As with all kexec tests, accidental success would be dangerous, so bogus inputs are essential.

Test signals: Output includes NULL case, raw pointer cases, decoded segment arrays with `...`, named kexec flags, and final exit.

Source read signal: complete file read for this research pass; file size 142 line(s), 4554 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kexec_load.c -->
