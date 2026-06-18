# sources/test-tools/syzkaller/dashboard/app/fix_test.go

Purpose: integration regression suite for fixed-bug lifecycle and fixing commit propagation.

Important APIs/types/functions: `TestFixBasic`, `TestFixedByTwoCommits`, `TestReFixed`, `TestFixTwoManagers`, `TestReFixedTwoManagers`, `TestFixedWithCommitTags`, `TestFixedDup`, `TestFixedDup2`, `TestFixedDup3`, plus `UploadBuild`, `ReportCrash`, `BuilderPoll`, `NeedRepro`, and `ReportingUpdate`.

Control flow: tests upload builds/crashes, mark bugs fixed through reporting updates or build-reported fix tags, verify builders receive pending commits until all relevant managers include them, and confirm new crashes after closure create sequenced bugs.

State/persistence: exercises persistent `Bug.Commits`, `CommitInfo`, `NeedCommitInfo`, `FixTime`, `LastActivity`, `PatchedOn`, duplicate/canonical status, and manager build commit state.

Dependencies/integration: spans reporting APIs, builder polling, crash ingestion, duplicate handling, build upload fix tag parsing, and datastore-backed test context.

Risks/test signals: fix data can arrive via users, builds, and duplicates; multi-manager closure and duplicate propagation are race-prone. Tests assert single/multi-commit fixes, re-fixing semantics, two-manager behavior, commit tag fixes, and duplicate edge cases.
