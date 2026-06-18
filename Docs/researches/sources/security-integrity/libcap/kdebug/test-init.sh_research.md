## sources/security-integrity/libcap/kdebug/test-init.sh

Purpose: init process for the kdebug initramfs that mounts basic filesystems, runs libcap quick tests, optionally opens an interactive shell, and exits QEMU.

Important APIs/functions: mount commands for proc/devtmpfs/sysfs/devpts, `quicktest.sh`, `sh -i`, and `./exit`.

Control flow: sets `PATH=/bin`, mounts required pseudo-filesystems, enters `/root`, runs quicktest and interactive shell when `/root/interactive` exists; otherwise runs quicktest and calls `./exit 1` on failure, then calls `./exit` for success.

State/persistence: mounts virtual filesystems in guest and runs tests; no disk persistence.

Dependencies/integration: generated initramfs layout from `test-kernel.sh`, busybox applets, libcap progs/tests, `exit` helper.

Risks: minimal error handling on mounts; failures before `exit` can leave QEMU running; interactive path depends on marker file.

Test signals: boot QEMU from `make -C kdebug test` and observe quicktest pass/fail exit.
