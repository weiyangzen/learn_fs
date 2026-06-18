<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-openbsd-vmm-worker.sh -->
# sources/test-tools/syzkaller/tools/create-openbsd-vmm-worker.sh

## Purpose

Builds minimal OpenBSD worker disk image.

## Important APIs, Types, and Functions

Snapshot ISO, install.site, generated ed25519 worker key, autoinstall config, growisofs, qemu-img, expect.

## Control Flow

Generates worker keys, injects minimal set/autoinstall files into patched ISO, installs to worker_disk.raw via QEMU/expect, prints host keys, and reports the disk.

## State and Persistence Behavior

Persists worker_disk.raw, worker_key files, ISO support files, install_log.

## Dependencies and Integration Points

Requires OpenBSD snapshots, QEMU/KVM, growisofs, expect, ssh-keygen.

## Risks and Edge Cases

Generated keys/password settings are for testing; snapshot prompt drift can break automation.

## Test Signals

Boot worker_disk.raw and verify SSH with worker_key plus minimal set selection.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-openbsd-vmm-worker.sh -->
