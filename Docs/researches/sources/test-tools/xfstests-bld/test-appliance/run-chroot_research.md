# sources/test-tools/xfstests-bld/test-appliance/run-chroot

Purpose: convenience helper to enter the generated `rootdir` chroot.

Important flow: set `ROOTDIR=$(pwd)/rootdir`, mount proc and sysfs into it, copy `/proc/mounts` to `etc/mtab`, `cd` into rootdir, run `chroot $ROOTDIR /bin/bash`, then unmount proc and sysfs.

State and dependencies: transient mounts under `rootdir/proc` and `rootdir/sys`; modifies `rootdir/etc/mtab`. Requires root privileges and a valid rootdir.

Integration points: useful for debugging `gen-image` output between stages.

Risks and test signals: if the chroot shell exits abnormally or the script is interrupted, mounts may remain. Tests are manual: enter/exit chroot and confirm mounts unmount cleanly.
