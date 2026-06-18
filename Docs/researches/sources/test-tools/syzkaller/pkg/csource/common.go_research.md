# sources/test-tools/syzkaller/pkg/csource/common.go

This file prepares the executor common header used as the template for generated C reproducers. Its central functions are `createCommonHeader`, `defineList`, `commonDefines`, and `removeSystemDefines`.

`createCommonHeader` computes feature and syscall defines, runs the target C preprocessor over `executor.CommonHeader` with `-nostdinc` and directive-preserving flags, strips compiler/system defines, applies placeholder replacements, normalizes syzkaller integer aliases to C stdint types, and removes `SYZ_HAVE_*` defines. `defineList` includes common feature macros plus syscall numbers used by the main and mmap setup programs. `commonDefines` maps `Options` and program-required features to `SYZ_*` preprocessor symbols.

State is transient source bytes and define lists; no persistence occurs. Dependencies include target CPP configuration, executor bundled headers, program feature extraction, runtime host OS, and target metadata. Integration is tight with `csource.go`, which supplies replacement values for process counts, syscalls, timeouts, sandbox entry, results, and generated call bodies.

Risks include silently ignoring preprocessor errors when stdout is non-empty, missing real CPP failures among expected `-nostdinc` include errors, stale macro lists, and replacement-token mismatches. Test signals include `TestExecutorMacros`, generated-source build tests, and syscall-generation fixtures that exercise comments and call expansion after common header preprocessing.
