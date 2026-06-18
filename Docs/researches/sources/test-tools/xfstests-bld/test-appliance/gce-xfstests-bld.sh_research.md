# sources/test-tools/xfstests-bld/test-appliance/gce-xfstests-bld.sh

Purpose: startup script run inside the temporary GCE image-build VM to install packages, unpack appliance files, build Go servers, configure services, clean state, and preserve the boot disk for image creation.

Important flow: redirect output to `/image-build.log`; install Debian packages/backports and optional Phoronix; rewrite apt suite if metadata requests it; configure serial/telnet gettys; fetch staged tarballs from GCS; unpack xfstests and root files; install Python requirements and drgn; configure lighttpd, test config, result directories, LVM discard, fsgqa users, systemd services, tmp mount, NFS service defaults, custom debs, gcloud components, and Go toolchain; build KCS and LTM binaries into `/usr/local/lib/bin`; label root filesystem, remove caches/SSH host keys, fstrim, and delete the build instance keeping boot disk.

State and dependencies: modifies the entire root filesystem of the build VM; uses metadata placeholders filled by `gce-create-image`; depends on apt, curl, gcloud storage, Go download, systemd, pip, tar, and xfstests-bld payloads.

Integration points: creates the runtime environment consumed by every GCE appliance script and Go server in this subset.

Risks and test signals: hardcoded Go version must be available for architecture. PEP 668 override and package names vary by Debian suite. The script deletes SSH host keys for later regeneration. Validation is image boot, service enablement, Go binary existence, and successful `gce-load-kernel`/`gce-setup` path on instances.
