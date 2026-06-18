# sources/test-tools/xfstests-bld/run-fstests/compress-rootfs

Purpose: recompresses the default KVM root filesystem qcow2 image by converting to raw, running filesystem discard, then converting back to compressed qcow2.

Important commands: `qemu-img convert -f qcow2 -O raw`, `e2fsck -fy -E discard`, `qemu-img convert -f raw -O qcow2 -o compat=0.10 -c`, and cleanup of the raw image.

Control flow/state: uses fixed paths under `./test-appliance`, creates `root_fs.raw`, rewrites `root_fs.img`, then removes the raw file.

Dependencies/integration: depends on qemu-img and e2fsck. Intended as maintenance utility for the test appliance image.

Risks: destructive overwrite of `root_fs.img`; no `set -e`, so a failed command may allow later commands to run. Fixed `DIR=.` means it must be run from repository/run-fstests context.

Test signals: final qcow2 should pass `qemu-img check` and boot under kvm-xfstests.
