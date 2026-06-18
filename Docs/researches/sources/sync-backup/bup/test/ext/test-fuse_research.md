## sources/sync-backup/bup/test/ext/test-fuse

Purpose: validates the FUSE view of a Bup repository.

Important control flow: skips if FUSE import/version, `fusermount`, or `/dev/fuse` access is unavailable. Creates a repo with two potential save timestamps, mounts `bup fuse -f`, checks branch/save/latest listings and file content, confirms new saves are not noticed by an existing mount, then remounts with `--meta` and verifies permissions, owner/group, and pre-epoch timestamp clamping.

State and dependencies: uses a live FUSE mount and cleanup trap. Depends on VFS, metadata public rendering, `stat`, and timezone UTC.

Risks covered: stale mount caching, metadata presentation, timestamp lower bound behavior, and mount cleanup.
