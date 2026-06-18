# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-load-kernel

Purpose: early boot script that installs or kexecs the kernel under test and unpacks test appliance overlays before normal test setup. It reads GCE metadata through `gce_attribute`, copies hooks and tarballs from GCS, updates `/run/test-env`, and either exits for stock-kernel runs, installs a Debian kernel package, or writes and executes `/root/do_kexec`.

Important flow: source `/usr/local/lib/gce-funcs`; optionally honor an existing `/root/do_kexec`; set the gcloud zone; fetch hooks, xfstests tarball, replacement `files.tar.gz`, and module tarball; read kernel/test metadata such as `kexec`, `kopt`, `cmd`, memory, CPUs, mount/disk options, fstest config/set/exclusions, API/string options, and NFS server mode. Non-kexec runs persist test parameters to `/run/test-env` and report the current kernel. `.deb` kernels update GRUB command line, install with retry while dpkg settles, select the matching grub menu entry, and reboot. Raw kernel images are copied to `/root/bzImage` and launched via `kexec`.

State and dependencies: writes `/root/hooks`, `/root/xfstests`, `/root/test-config`, `/run/test-env`, `/root/kernel-deb.deb`, `/root/bzImage`, `/root/do_kexec`, and GRUB drop-ins. It depends on GCE metadata, GCS helpers, `tar`, `depmod`, `dpkg`, `grub-reboot`, `kexec`, `systemctl`, and `fuser`.

Integration points: hands environment to `gce-setup`, invokes `run_hooks kexec`, uses `gce-add-metadata` for kernel status, and transforms device names in uploaded `files.tar.gz` configs for GCE mapper devices.

Risks and test signals: metadata values are interpolated into kernel command lines and shell fragments, so quoting and trusted inputs matter. Debian package menu parsing is brittle against GRUB output. Kexec failures stop the test appliance. Evidence is mostly integration-level: serial logs, metadata status, `/run/test-env`, and successful transition into `gce-setup`.
