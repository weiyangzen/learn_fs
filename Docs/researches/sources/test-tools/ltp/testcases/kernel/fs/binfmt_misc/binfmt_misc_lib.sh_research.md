# sources/test-tools/ltp/testcases/kernel/fs/binfmt_misc/binfmt_misc_lib.sh

Purpose: shared LTP shell library for binfmt_misc tests. It handles setup, cleanup, mount discovery, module loading, and binary type removal.

Important APIs/types/functions: `TST_SETUP`, `TST_CLEANUP`, `TST_NEEDS_DRIVERS`, `TST_NEEDS_TMPDIR`, `TST_NEEDS_ROOT`, `TST_NEEDS_CMDS`, globals `rmod_binfmt_misc`, `umount_binfmt_misc`, `binfmt_misc_mntpoint`, functions `remove_binary_type`, `get_binfmt_misc_mntpoint`, `binfmt_misc_setup`, and `binfmt_misc_cleanup`.

Control flow: setup checks `/proc/filesystems` and loads `binfmt_misc` with `modprobe` if needed. It then checks `/proc/mounts` for an actual `binfmt_misc` mount and, if absent, creates and mounts `ltp_binfmt_misc`. Cleanup unmounts only if this library mounted it, removes the mount directory, and unloads the module only if setup loaded it.

State/persistence behavior: may load/unload the kernel module, mount/unmount a binfmt_misc filesystem, create/remove a temporary mount directory, and remove binfmt entries by writing `-1` to their control files.

Dependencies/integration: depends on LTP `tst_test.sh`, root privileges, `modprobe`, `mount`, `umount`, `mkdir`, and `rm`.

Risks/test signals: cleanup tracks ownership through flags to avoid disturbing preexisting mounts/modules. Incorrect mount detection could leave a mount behind or affect a system binfmt_misc instance.
