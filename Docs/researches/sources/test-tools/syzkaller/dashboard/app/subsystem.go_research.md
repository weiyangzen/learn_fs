# sources/test-tools/syzkaller/dashboard/app/subsystem.go

Purpose: automatic subsystem assignment and maintainer lookup for dashboard bugs. It refreshes bug subsystem labels from the configured `subsystem.Service`, preserves user-set labels, and exposes helpers for subsystem links and maintainer lists.

Important APIs and types: `reassignBugSubsystems`, `bugsToUpdateSubsystems`, `checkOutdatedSubsystems`, marker types `autoInference` and `updateRevision`, `updateBugSubsystems`, `logSubsystemChange`, constants `crashesForInference` and `openBugsUpdateTime`, `inferSubsystems`, `subsystemMaintainers`, `getSubsystemService`, and `subsystemListURL`.

Control flow: `reassignBugSubsystems` exits when the namespace has no subsystem service. Otherwise it queries candidate bugs in priority order: open bugs with stale revision, open bugs older than the periodic refresh interval, fixed bugs with stale revision, then all remaining stale revisions. User-subsystem bugs are not overwritten; they are checked for obsolete names and stamped with the latest revision. Auto-assigned bugs load up to seven crashes, convert guilty files and syz repro text into `subsystem.Crash` records, run `Service.TracedExtract`, and update labels/time/revision. Changes are logged when the sorted subsystem name set differs.

State and persistence: reads namespace config and datastore `Bug`/`Crash` entities plus repro text blobs. Mutates `Bug` labels, `SubsystemsRev`, and `SubsystemsTime` through `updateSingleBug`. User labels are preserved, but stale revision is still recorded to avoid repeat processing.

Dependencies and integration points: `pkg/subsystem`, `debugtracer`, App Engine datastore/logging, dashboard bug label APIs (`LabelValues`, `SetAutoSubsystems`, `hasUserSubsystems`), crash query/text helpers, and app URL generation. Cron endpoint `/cron/refresh_subsystems` in surrounding app code likely calls `reassignBugSubsystems`.

Risks: query priority can return duplicate bugs across query classes if earlier results do not exhaust `count`; callers need to tolerate possible repeated updates. Inference uses only the first guilty file per crash and up to seven crashes, so broad or later evidence can be missed. Missing repro text aborts inference. User subsystem labels that no longer exist are only logged, not repaired.

Test signals: `subsystem_test.go` validates maintainer lookup, revision and time-based refresh, closed/invalid bug refresh, preservation of user labels, no overwrite when later repros point elsewhere, and monthly subsystem report behavior built on assigned labels.
