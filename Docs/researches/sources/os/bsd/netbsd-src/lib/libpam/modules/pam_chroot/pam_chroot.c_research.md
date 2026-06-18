# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_chroot/pam_chroot.c

Session module that chroots users on session open. It gets the PAM user, resolves passwd data, skips root unless `also_root` is set, and chooses the chroot/cwd from a `/./` marker in the home directory or `dir`/`cwd` options.

If `always` is set and no chroot is available, it fails. On success it calls `chroot`, `chdir`, and updates PAM `HOME` to the post-chroot cwd. Close session is a no-op success.
