<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/debian/prerm -->
# sources/sync-backup/git-lfs/debian/prerm

## Research

This Debian pre-removal script runs `git lfs uninstall --skip-repo --system`. It removes system-level Git LFS configuration while avoiding repository-local changes in `/`, preserving user intent if replacing the package with another installation.

There is no local state or control flow. Persistent effects are system Git config/filter removal. Dependencies mirror `postinst`: `/bin/sh`, `git-lfs`, Git, and permissions. Risks include uninstall failure blocking package removal and assumptions that system config should be removed for every pre-removal action.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/debian/prerm -->
