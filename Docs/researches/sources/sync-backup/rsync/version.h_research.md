# sources/sync-backup/rsync/version.h

Purpose: build-time version constants for rsync.

Important declarations: `RSYNC_VERSION` is `"3.5.0dev"`. `MAINTAINER_TZ_OFFSET` is `10.0`, used by maintainer/build tooling that needs the maintainer timezone offset.

Control flow and state: no code or persistence. The header is consumed by `usage.c`, where `rsync_version()` may prefer `RSYNC_GITVER` and strips a leading `v`.

Dependencies and integration: included in version/help output and any generated release metadata. Risks are simple but user-visible: stale or malformed version strings affect protocol/support reporting and test expectations around `--version`. Test signals are version-output checks and build packaging validation.
