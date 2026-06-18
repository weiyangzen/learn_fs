<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_f.c -->
# sources/test-tools/strace/tests/ioctl_fs_f.c

Purpose: `ioctl_fs_f.c` FS_IOC{,32}_{G,S}ETFLAGS decoder test for legacy filesystem inode flags. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC32_GETFLAGS, FS_IOC32_SETFLAGS, FS_IOC_GETFLAGS, FS_IOC_SETFLAGS, FS_*_FL flags, _IO('f',0xff) fallback. Local include directives/macros observed in this source are `tests.h, linux/fs.h, errno.h, stdio.h, sys/ioctl.h` and `VALID_FLAGS=0xf2ffffff, INVALID_FLAGS=0xd000000`. Locally visible function entry points include `do_ioctl, do_ioctl_ptr, main`.

Control flow: main iterates command descriptors, skipping duplicate 32-bit/native aliases when equal, then tests NULL/0, bad pointer, invalid flag word for set commands, valid flag word for set commands, and pointer-only get commands. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fs_f.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; one tail-allocated unsigned int is mutated for flags. There is no injected-return path in this file. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fs.h, sys/ioctl.h, XLAT mode macros. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: architecture aliases between native and 32-bit commands, filesystem flag table additions, and xlat mode rendering changes. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates duplicate skipping, on-enter vs on-exit argument policy, known/unknown FS flag printing, and fallback command formatting. This file has 129 source lines and 3076 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fs_f.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fs_f.c -->
