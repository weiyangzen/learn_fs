# File Research: sources/local-fs/e2fsprogs/misc/fsck.8.in

## Purpose
Manpage source for generic `fsck`, the Linux filesystem-check dispatcher.

## Key Elements
Explains that `fsck` is a front-end for filesystem-specific checkers named `fsck.<fstype>`. Documents serial and parallel checking, `/etc/fstab` traversal, pass-number ordering, root filesystem handling, progress reporting, mounted-filesystem skipping, dry-run mode, type filtering, and pass-through filesystem-specific options.

Defines exit status bit meanings and notes that multiple filesystem results are ORed. Documents environment variables `FSCK_FORCE_ALL_PARALLEL`, `FSCK_MAX_INST`, `PATH`, and `FSTAB_FILE`.

## Dependencies
References `/etc/fstab`, checker search paths, e2fsck and many filesystem-specific fsck tools.

## Behavior/Risks
Warns that arbitrary fs-specific option forwarding is intentionally limited and that parallel interactive checks can be unsafe. Also calls out risk of checking root in parallel with other filesystems.
