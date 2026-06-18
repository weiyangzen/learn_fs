# sources/test-tools/syzkaller/dashboard/app/stats.go

Purpose: collects bug-level statistics for syzbot reporting stages and converts dashboard datastore objects into `syzbotstats.BugStatSummary` objects.

Important APIs and types: `bugInput` bundles `Bug`, selected `BugReporting`, reported `Crash`, and `Build`; methods/functions include `fixedAt`, `bugStatus`, `allBugInputs`, generic `getAllMulti[T]`, and `getBugSummaries`.

Control flow: `allBugInputs` loads all bugs in a namespace, selects `lastReportedReporting`, asynchronously batches crash dependencies for reporting records with a `CrashID`, then batches corresponding build dependencies. `getBugSummaries` filters bugs that reached the requested reporting stage, builds summary fields from bug/crash/build state, includes all external reporting IDs and fix hashes, optionally adds repro and cause-bisection timestamps, prefers fixing commit dates over close time when earlier, computes status, estimates hits per day for enough/fresh crashes, and copies subsystem label values.

State and persistence: reads datastore `Bug`, child `Crash`, and `Build` entities; it does not mutate state. `getAllMulti` works around App Engine datastore multi-get limits by chunking at 1000 keys and returns the first failing key for `MultiError` cases.

Dependencies and integration points: App Engine datastore, `loadAllBugs`, `dependencyLoader`, `lastReportedReporting`, `buildKey`, `bugReportingByName`, `queryBestBisection`, `dashapi.CrashFlags`, and `syzbotstats`. The output feeds statistics generation outside this file.

Risks: `bugStatus` returns an error for unexpected status combinations, which can fail the entire summary generation for one malformed bug. The `HitsPerDay` guard appears inverted against its comment: it computes when crashes are at least the minimum or the span is short, so careful review is needed before changing. Missing crash/build dependencies abort the entire load. Summary correctness depends on `lastReportedReporting` and stage names matching config.

Test signals: no dedicated test in this subset, but reporting tests create the same bug/crash/build/reporting states. Stats behavior should be tested with fixed, dup, invalid, auto-invalidated, bisection, repro, and subsystem-labeled bugs.
