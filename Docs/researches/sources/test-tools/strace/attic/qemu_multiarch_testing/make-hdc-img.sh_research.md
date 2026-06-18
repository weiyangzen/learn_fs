<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/attic/qemu_multiarch_testing/make-hdc-img.sh -->
# sources/test-tools/strace/attic/qemu_multiarch_testing/make-hdc-img.sh

Purpose: creates an ext3 `hdc.img` disk image from the `hdc.dir` directory for QEMU multi-architecture testing.

Important functions and commands: `cleanup()` unmounts and removes temporary mount directory. The script computes source size with `du`, creates a sparse-ish image using `dd` with seek, formats it with `mkfs.ext3`, disables periodic checks using `tune2fs`, loop-mounts it, copies `hdc.dir/*`, and unmounts.

Control flow: `sh -ex` with traps for normal exit and signals. It refuses to run if `hdc.img.dir` exists.

State and persistence: creates `hdc.img` and temporary `hdc.img.dir`; removes temporary mount directory on cleanup.

Dependencies and integration: requires root or mount privileges, ext3 tools, loop devices, and the `hdc.dir` source tree with init scripts.

Risks: loop mounting and `rm -rf hdc.img.dir` require careful cwd. Size is only twice `du -ks`, which may be too small for later build expansion. Test signals: run script under appropriate privileges, run `fsck`/`debugfs` or mount the image, and verify init files are present.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/attic/qemu_multiarch_testing/make-hdc-img.sh -->
