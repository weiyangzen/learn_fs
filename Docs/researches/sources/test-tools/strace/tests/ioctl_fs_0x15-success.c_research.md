<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_0x15-success.c -->
# sources/test-tools/strace/tests/ioctl_fs_0x15-success.c

Purpose: `ioctl_fs_0x15-success.c` linux/fs.h 0x15 ioctl decoder test for filesystem UUID, sysfs path, and logical block metadata capability commands. Wrapper chain: ioctl_fs_0x15-success.c -> ioctl_fs_0x15.c. Variant effect: INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC_GETFSUUID, FS_IOC_GETFSSYSFSPATH, FS_IOC_GETLBMD_CAP, struct fsuuid2, fs_sysfs_path, logical_block_metadata_cap, LBMD_PI_* flags/types. Local include directives/macros observed in this source are `ioctl_fs_0x15.c` and `INJECT_RETVAL=42`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip uses an unknown _IO(0x15,0xff) command; main emits hex-arg fallback cases, NULL and bad-pointer checks for the three known commands, then exercises UUID length boundaries, path length/string termination, and valid/invalid LBMD cap flags/types. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fs_0x15.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; tail-allocated structs are filled and mutated. INJECT_RETVAL makes output-side structures printable with injected suffixes. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fs.h, sys/ioctl.h, XLAT macros, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: new fs.h 0x15 commands, structure field changes, string length boundaries, and LBMD enum drift affect expected output. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Exact output checks command fallback, NULL/bad pointer behavior, length-capped quoted data, known/unknown LBMD flags, and injection locking. This file has 3 source lines and 52 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fs_0x15-success.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_0x15-success.c -->
