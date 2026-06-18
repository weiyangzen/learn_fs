# sources/test-tools/syzkaller/pkg/mgrconfig/testdata/qemu.cfg

Purpose: Compact QEMU canned config fixture used by `TestCanned`.

Important content: Defines target `linux/amd64`, HTTP host, workdir, kernel object path, testdata disk image, syzkaller path, disabled key-management syscalls, suppressions, procs 4, type `qemu`, and VM settings for count, CPU, memory, kernel, and initrd.

Control flow and state: Loaded and completed by mgrconfig, then VM raw config parsed into `qemu.Config`.

Dependencies and integration: Exercises disabled syscall list parsing, suppressions, QEMU kernel/initrd fields, and path normalization.

Risks: Absolute kernel/workdir paths are placeholders; completion does not require kernel object existence in this fixture path set.

Test signals: Positive fixture for common Linux QEMU manager configuration.
