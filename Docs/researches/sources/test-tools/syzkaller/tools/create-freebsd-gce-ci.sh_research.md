<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-freebsd-gce-ci.sh -->
# sources/test-tools/syzkaller/tools/create-freebsd-gce-ci.sh

## Purpose

Builds a FreeBSD GCE image that starts syz-ci.

## Important APIs, Types, and Functions

Downloads FreeBSD VM raw image, generated setup/rc scripts, mkisofs, expect, QEMU, tar packaging.

## Control Flow

Expands disk, builds config ISO, boots QEMU, logs in over serial, mounts ISO, runs setup to install packages/SSH/console/syzkaller dir, powers off, and archives disk for GCE upload.

## State and Persistence Behavior

Creates disk.raw/image.iso/setup.sh/rc.local/install_log/final tarball; booted image later clones syzkaller and runs syz-ci.

## Dependencies and Integration Points

Requires FreeBSD image URL, QEMU, expect, mkisofs, package repos, `id_ed25519.pub`, GCE metadata at runtime.

## Risks and Edge Cases

Hard-coded version/prompt/package assumptions are brittle; root SSH by key and cloud rc logic are CI-specific.

## Test Signals

Complete QEMU install, inspect log, boot disk locally, verify syz-ci starts.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/create-freebsd-gce-ci.sh -->
