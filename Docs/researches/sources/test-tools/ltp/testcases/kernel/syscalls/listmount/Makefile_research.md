# sources/test-tools/ltp/testcases/kernel/syscalls/listmount/Makefile

Purpose: builds `listmount` syscall tests. It includes standard LTP testcase rules and generic leaf target rules without extra libraries. Runtime feature gating appears in the C files through minimum kernel versions and raw syscall wrappers. Integration points are `lapi/mount.h`, `lapi/syscalls.h`, namespace/mount helpers, and statx support. Risks are older kernels lacking `listmount`. Test signal is successful compilation of the listmount test binaries.
