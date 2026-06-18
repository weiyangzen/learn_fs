# sources/security-integrity/gocryptfs/contrib/cleanup-tmp-mounts.sh

Purpose: This helper script cleans up leftover temporary gocryptfs/FUSE mounts from tests or manual runs.

Important APIs and steps: It scans mount output for project test paths and invokes unmount helpers such as `fusermount`, `umount`, or project scripts.

Control flow and state: It mutates system mount state by unmounting matching paths. No persistent repository state is written.

Dependencies and integration points: Used by developers and test wrappers to recover from interrupted FUSE tests.

Risks and test signals: Mount matching must be conservative to avoid unmounting unrelated filesystems. Signal is successful removal of stale project mounts without affecting unrelated mounts.
