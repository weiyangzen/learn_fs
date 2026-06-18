# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/kcs/bisect.go

Purpose: KCS-side Git bisect coordinator. It owns one cloned repository per bisect, builds each candidate commit, dispatches LTM tests, records test history, aggregates final results, uploads a bisector tarball, and emails a summary.

Important APIs/types: `GitBisector` stores request metadata, repository, bad/good commits, log/result directories, history, timeout channel, and status. Main methods are `Start`, `Step`, `Finish`, `Build`, `StartTest`, `Clean`, `Info`, and `CheckActive`. Package functions `RunBisect` and `BisectorStatus` route internal LTM requests and expose active state.

Control flow: `RunBisect` creates a bisector for `LTMBisectStart` or looks one up for `LTMBisectStep`, validates commit identity, advances git bisect, then loops building and skipping build-error commits until a testable commit is built. `Build` sets a one-run kernel GCS path, updates `TaskRequest` fields for LTM, and calls `RunBuild` or `MockRunBuild`. `Finish` aggregates per-step LTM results from GCS, packs a combined tarball, deletes per-step result objects, emails, and cleans.

State and dependencies: global `bisectorMap` protected by `bisectorLock`; per-bisect repo under `/cache/repositories`; logs in `logging.KCSLogDir`; GCS result objects; SendGrid email. It depends on `util/git`, `util/gcp`, `util/server`, `gce-xfstests get-results`, `tar`, and `xz`.

Risks and test signals: state is in-memory, so server restart loses active bisects. `Clean` sends on `done` while called under lock and after log closure paths; double cleanup would panic. Commit validation mutates missing `origin/` prefixes. Existing tests cover only a small bisect start path, so integration tests around KCS/LTM round trips, build-error skips, and cleanup are important.
