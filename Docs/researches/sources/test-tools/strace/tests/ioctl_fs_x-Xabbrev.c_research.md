<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_x-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_fs_x-Xabbrev.c

Purpose: `ioctl_fs_x-Xabbrev.c` linux/fs.h X-command ioctl decoder test for freeze/thaw, trim, fsxattr, and shutdown flags. Wrapper chain: ioctl_fs_x-Xabbrev.c -> ioctl_fs_x.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output.

Important APIs/types/functions: Primary APIs and data surfaces are FIFREEZE, FITHAW, FITRIM, FS_IOC_FSSETXATTR, FS_IOC_FSGETXATTR, FS_IOC_SHUTDOWN, struct fstrim_range, fsxattr, FS_XFLAG_* from test_fs_xflags.h, FS_SHUTDOWN_FLAGS_*. Local include directives/macros observed in this source are `ioctl_fs_x.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip locks on FIFREEZE; main emits simple no-arg and unknown X command cases, NULL cases, FITRIM struct, FSSETXATTR known/unknown xflags, FSGETXATTR failure/success split, and FS_IOC_SHUTDOWN known/unknown flags. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fs_x.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; tail-allocated structs are filled and reused. INJECT_RETVAL appends injected status and enables output-side get decoding. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fs.h, test_fs_xflags.h, sys/ioctl.h, ioctl-success.sh for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: filesystem flag additions, shutdown flag additions, injected return synchronization, and native type sizes can alter expected output. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks no-arg formatting, pointer faults, range/fsxattr field decoding, known/unknown flags, and injection markers. This file has 3 source lines and 46 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fs_x-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_x-Xabbrev.c -->
