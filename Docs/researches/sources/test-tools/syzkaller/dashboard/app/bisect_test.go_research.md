# sources/test-tools/syzkaller/dashboard/app/bisect_test.go

Purpose: broad integration test coverage for syzbot bisection workflows, including cause/fix job selection, job completion reporting, email formatting, external reporting, reliability flags, UI display, and admin invalidation.

Important tests and helpers: `TestBisectCause` is the main scenario: it verifies no bisection without repros, cause job ordering by repro quality/time/manager, failed and successful cause bisections, email links for logs/configs/repros, CC filtering, upstream propagation of bisection results, delayed fix bisections, and no extra jobs. `TestBisectCauseInconclusive`, `TestBisectCauseAncient`, and syz-repro variants cover inconclusive result rendering. `TestUnreliableBisect` and `TestBisectWrong` verify release/merge/noop/ignore flags suppress reporting and CC side effects as intended. `TestBisectCauseExternal` and `TestBisectFixExternal` verify API-poll reporting and fix-bisection auto-close. UI/admin tests assert bisection results and status show on pages, invalidated jobs are hidden, and restart reopens cause bisection. Helpers `addBuildAndCrash`, `addBisectCauseJob`, and `addBisectFixJob` set up reusable datastore/job/email state.

Control flow under test: tests move through build upload, crash reporting, email polling, job polling, `JobDone`, incoming `#syz` commands, time advancement, external `ReportingPollBugs`, and admin GET actions. They verify both immediate report emails and later report-stage emails include or suppress bisection sections based on result flags.

State and persistence behavior: exercises persisted `Bug`, `Crash`, `Build`, and `Job` entities, text blobs behind external links, `Bug.BisectCause`/fix status, bug commit lists, reporting state, and `Job.InvalidatedBy`.

Dependencies and integration points: depends on dashapi job/report types, email command processing, external link storage, reporting configuration, manager polling, admin handlers, datastore queries, and UI templates.

Risks covered: incorrect job prioritization, leaking syzbot addresses into CC, unreliable bisection results being treated as authoritative, missing bisection data in later reporting stages, automatic closure mistakes, and stale invalidated bisections in UI. Gaps are mostly around true concurrency and real worker-side bisection behavior.
