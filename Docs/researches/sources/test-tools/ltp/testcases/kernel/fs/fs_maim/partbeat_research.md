# sources/test-tools/ltp/testcases/kernel/fs/fs_maim/partbeat

Purpose: Perl helper that formats a partition, fscks it, repeatedly mounts/unmounts it while creating marker files, fscks again, and leaves it mounted with markers removed.

Important APIs/types/functions: filesystem-specific `mkfs` command selection, `fsck -t`, `mount -t`, `umount`, `touch`, target device parsing, and iteration loop.

Control flow: chooses `mkfs.jfs`, `mkfs`, `mkfs -t ext3`, or `mkreiserfs` based on the requested filesystem type, runs fsck, creates a mount directory named after the device basename, then for each iteration mounts the partition, touches `indicatorN`, and unmounts. Finally it fscks again, mounts once more, and removes indicators.

State/persistence behavior: destroys and recreates the filesystem on the target partition, creates a local mount directory, creates/removes indicator files, and leaves the filesystem mounted at the end for `backbeat`.

Dependencies/integration: invoked by `maimparts` for each generated partition. Depends on root, mkfs/fsck variants, mount/umount, and writable current directory.

Risks/test signals: command outputs are printed but exit statuses are not robustly enforced. Device basename directory conflicts can affect results. Success is inferred from clean command output and availability of the mounted partition for subsequent tests.
