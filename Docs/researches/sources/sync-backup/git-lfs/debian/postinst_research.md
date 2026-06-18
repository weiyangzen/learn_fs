<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/debian/postinst -->
# sources/sync-backup/git-lfs/debian/postinst

## Research

This Debian maintainer script runs `git lfs install --skip-repo --system` after package installation. Its purpose is to install system-level Git LFS filters/hooks while avoiding accidental mutation of `/` if the root directory happens to be a Git repository.

The script has no branching or local state. Persistent effects are system Git config/filter installation performed by `git lfs install`. Dependencies are `/bin/sh`, the packaged `git-lfs` binary, Git, and sufficient privileges for system config. Risks are install-time failure propagating to package configuration, path lookup of `git`, and behavior changes in `git lfs install`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/debian/postinst -->
