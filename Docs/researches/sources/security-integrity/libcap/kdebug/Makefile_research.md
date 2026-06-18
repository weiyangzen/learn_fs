## sources/security-integrity/libcap/kdebug/Makefile

Purpose: make wrapper for libcap kernel/debug testing via a generated initramfs and QEMU.

Important targets: `test`, `shell`, `exit`, `all`, `install`, and `clean`.

Control flow: `test` builds static `exit`, removes `interactive`, and runs `test-kernel.sh`; `shell` creates `interactive` before running the same script; `exit` builds `exit.c` statically; `clean` removes generated initramfs/config/output files.

State/persistence: creates `exit`, `interactive`, `fs.conf`, and `initramfs.img`; invokes broader tree build/test.

Dependencies/integration: top-level `Make.Rules`, C compiler, static libc, `test-kernel.sh`, local Linux kernel tree.

Risks: target assumes cwd is `kdebug`; static build may fail if static libc unavailable; `clean` deletes `interactive`, changing shell/test mode.

Test signals: `make -C kdebug test` for noninteractive QEMU run and `make -C kdebug shell` for interactive debug.
