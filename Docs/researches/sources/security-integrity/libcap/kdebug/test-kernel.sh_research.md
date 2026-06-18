## sources/security-integrity/libcap/kdebug/test-kernel.sh

Purpose: builds libcap, a Linux kernel, a test initramfs, and runs QEMU for capability/kernel integration testing.

Important APIs/functions: `die()`, `make LIBCSTATIC=yes clean all test`, `make -C progs tcapsh-static`, `make -C tests uns_test`, kernel `make V=1 all`, generated `fs.conf`, `gen_init_cpio`, `gzip`, and `qemu-system-$(uname -m)`.

Control flow: records interactive marker intent, rebuilds libcap static/test artifacts, builds the kernel under `../../linux`, generates an initramfs manifest containing init scripts, passwd, busybox links, libcap tools/tests, optional local `extras.sh`, and optional interactive marker, creates `initramfs.img`, computes bzImage path, and boots QEMU with serial console, SMP, and isa-debug-exit.

State/persistence: writes `fs.conf` and `initramfs.img`; builds libcap, tests, and kernel artifacts.

Dependencies/integration: local Linux kernel source at `../../linux`, kernel config already prepared, busybox at `/usr/sbin/busybox`, QEMU, gen_init_cpio, gzip, static libcap builds.

Risks: script references `HERE` before assignment when checking interactive marker, so preserving interactive mode may be unreliable; hardcoded paths and architecture assumptions; full kernel build is expensive.

Test signals: QEMU exit status, serial quicktest output, successful generation of initramfs, and optional interactive shell.
