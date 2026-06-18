# sources/test-tools/xfstests-bld/test-appliance/gen-image

Purpose: local root filesystem/image builder for the xfstests appliance, using debootstrap and optional fakechroot/fakeroot.

Important flow: parse output tar/image/update/resume/suite/mirror/networking/drgn/log/source-date/package options; choose suite from build metadata; optionally re-exec under `script`, fakechroot, or fakeroot; compute package list; define helpers for staging xfstests, symlink repair, final qcow2 conversion, cleanup, chroot execution, and abort cleanup. It formats/mounts a raw ext4 image unless fakechroot, binds apt/deb caches, runs debootstrap and optional second stage for foreign chroots, installs backports/manual debs, copies xfstests appliance files, creates device/mount directories and fsgqa users, configures systemd gettys/services, prunes docs/logs, handles fakechroot device nodes, optionally installs drgn, emits a deterministic tarball, converts raw to qcow2, and cleans.

State and dependencies: `rootdir`, raw/qcow2 images, apt cache directories, `debs`, `var.cache.apt.archives`, `var.lib.apt.lists`, and output tar/image. Depends on root privileges or fakechroot, debootstrap, qemu-img, mke2fs/e2fsck, chroot, tar, and systemd files inside rootfs.

Integration points: non-GCE image path parallel to `gce-create-image`; shares appliance `files/` payload and xfstests tarball.

Risks and test signals: cleanup uses mounts and can leave loop/bind mounts on interruption. Fakechroot handling is complex. Resume stages require operator accuracy. Tests should validate generated tar/image bootability and idempotent cleanup after failures.
