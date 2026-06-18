# sources/sync-backup/git-lfs/lfs/gitscanner_remotes.go

Purpose: computes remote refs to exclude or explicitly skip when scanning objects to push.

Important APIs/types/functions: `calcSkippedRefs`.

Control flow: loads cached remote branch refs and actual remote branch refs, builds a set of actual names, and returns `^<sha>` entries for cached refs still present on the remote.

State/persistence behavior: read-only remote/ref queries. Network access may occur through `git.RemoteRefs` depending on Git helper behavior.

Dependencies/integration: used by `NewGitScannerForPush` range-to-remote scans to avoid assuming deleted remote branches still protect objects.

Risks/test signals: errors from `CachedRemoteRefs` and `RemoteRefs` are ignored, resulting in empty or partial skips. Comments indicate this is a conservative strategy around remote garbage collection.
