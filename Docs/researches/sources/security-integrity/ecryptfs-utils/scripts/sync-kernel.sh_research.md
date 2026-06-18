# sources/security-integrity/ecryptfs-utils/scripts/sync-kernel.sh

Purpose: synchronizes eCryptfs kernel code from a Linux tree into legacy ecryptfs-kernel-git version directories.

Important APIs/commands: sources current version, copies `linux-git/fs/ecryptfs/*.[ch]`, applies a netlink patch and backpatches to create 2.6.18/17/16 directories.

Control flow/state: removes old kernel version directories, renames/copies `src`, and applies patches in sequence.

Dependencies/integration: requires sibling `linux-git`, `ecryptfs-kernel-git`, patches, and current version directory.

Risks: destructive to kernel mirror directories; no robust error handling around patch failures.

Test signals: patched version directories and patch command success.
