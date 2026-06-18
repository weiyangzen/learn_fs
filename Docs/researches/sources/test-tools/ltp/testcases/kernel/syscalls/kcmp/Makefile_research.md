# sources/test-tools/ltp/testcases/kernel/syscalls/kcmp/Makefile

Purpose: builds the `kcmp` syscall tests. It includes standard LTP testcase rules, adds `CFLAGS += -Wl,-z,now`, and delegates targets to `generic_leaf_target.mk`. There are no target-specific libraries or runtime state; the linker flag forces immediate symbol binding, likely to keep tests deterministic under the old harness. Integration points are LTP headers and Linux `kcmp` wrappers in the C files. Risks are platform/toolchain support for `-z now`. Test signal is successful build of `kcmp01`, `kcmp02`, and `kcmp03`.
