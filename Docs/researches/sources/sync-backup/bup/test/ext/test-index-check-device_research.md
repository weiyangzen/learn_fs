## sources/sync-backup/bup/test/ext/test-index-check-device

Purpose: root-only test for device-number sensitivity in index change detection.

Important control flow: skips unless root and loop filesystem tools are available. It creates an ext filesystem image, mounts copies through loopback and bind mounts, indexes one device as fake-valid, then remounts identical content from another device. Default indexing reports modified entries; `--no-check-device` treats them unchanged.

State and dependencies: mounts and unmounts loop filesystems and bind mounts. Depends on root privileges, `losetup`, `mke2fs`, `mount`, and `umount`.

Risks covered: index invalidation across device changes and user-controlled relaxation with `--no-check-device`.
