<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/uid_unix.go -->
# sources/sync-backup/restic/internal/restic/uid_unix.go

## Purpose
Converts OS user/group information into numeric uid/gid values on Unix-like platforms.

## Important APIs and Control Flow
`UidGidInt` parses `user.User.Uid` and `Gid` with `strconv.ParseUint` and returns `uint32` values. Control flow is a pair of parse operations with early return on invalid uid, then gid parsing.

## State, Persistence, Dependencies, and Integration
No state is persisted. It integrates with restore/backup metadata handling that needs numeric ownership on Unix platforms and depends on Go's `os/user` package.

## Risks and Test Signals
Risks are platform user database oddities and overflow/parse failures, which are surfaced to callers. Windows has a separate stub because uid/gid semantics do not apply.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/uid_unix.go -->
