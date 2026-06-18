# sources/security-integrity/ecryptfs-utils/scripts/rebuild-patches.sh

Purpose: regenerates backpatch diffs from the current kernel eCryptfs version to legacy kernel directories.

Important APIs/commands: sources `current-version.sh`, cleans multiple kernel version trees, copies `ecryptfs-kernel-git`, swaps `src` to version-specific directories, runs `diff -Naur`, and writes backpatch files under `backpatches/`.

Control flow/state: destructive cleanup and temporary clone directories in the caller's parent layout.

Dependencies/integration: assumes `ecryptfs-kernel-git` with version directories 2.6.16/17/18 and `$ECRYPTFS_VERSION`.

Risks: repetitive unquoted `rm -rf`, hard-coded kernel versions, and no `set -e`, so partial failures can still produce misleading patches.

Test signals: generated patch files and clean temporary directories.
