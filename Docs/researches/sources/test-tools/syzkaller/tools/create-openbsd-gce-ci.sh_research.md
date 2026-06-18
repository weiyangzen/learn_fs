<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-openbsd-gce-ci.sh -->
# sources/test-tools/syzkaller/tools/create-openbsd-gce-ci.sh

## Purpose

Builds OpenBSD GCE syz-ci image from snapshots.

## Important APIs, Types, and Functions

OpenBSD snapshot discovery, custom site set, autoinstall config, growisofs, qemu-img, expect, tar/gcloud instructions.

## Control Flow

Downloads ISO, injects site/autoinstall/disklabel/boot/random files, runs installer in QEMU, installs packages/configures syzkaller mount and syz-ci rc.local, verifies `pkg_add OK`, archives disk.raw.

## State and Persistence Behavior

Creates ISO/site/autoinstall/disklabel/disk.raw/install_log/tarball artifacts.

## Dependencies and Integration Points

Requires OpenBSD mirrors, QEMU/KVM, expect, growisofs, network packages, GCE metadata at runtime.

## Risks and Edge Cases

Moving snapshots and installer prompts are brittle; embedded test credentials/keys are CI-only.

## Test Signals

Run installer, verify package marker, boot image, confirm syz-ci and serial console.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-openbsd-gce-ci.sh -->
