# sources/test-tools/syzkaller/dashboard/app/repro_test.go

Purpose: integration tests for reproducer request policy, failed reproducer accounting, log-to-reproduce task selection, reproduction logs for mismatched titles, and manually submitted reproduction tasks.

Important APIs and helpers: `testNeedRepro1/2/3`, `normalCrash`, `dupCrash`, `closedCrash`, `closedWithReproCrash`, `TestNeedReproMissing`, `TestNeedReproIsolated`, `TestFailedReproLogs`, `TestLogToReproduce`, `TestReproForDifferentCrash`, and `TestReproTask`. The tests drive `ReportCrash`, `NeedRepro`, `ReportFailedRepro`, `LogToRepro`, and `ReproTaskDone`, plus admin form submission to `/test1/manager/<manager>` with `send-repro`.

Control flow: the main scenarios upload crashes with no repro, syz repro, and C repro and verify the `NeedRepro` bit returned from both `ReportCrash` and `NeedRepro`. Variants exercise normal bugs, duplicates, invalid/closed bugs, and closed bugs with existing reproducers. Failed-repro loops advance the mocked time to verify daily retry throttling. `TestNeedReproIsolated` directly checks `needReproForBug` on hand-built `Bug` values for corrupted/suppressed titles, syz-only repros, stale C repros, failed attempt limits, SYZFATAL/SYZFAIL exceptions, and revoked repro state.

State and persistence: failed repro attempts store bounded `ReproAttempts` with text blobs for logs; when `maxReproLogs` is exceeded, the oldest text object must be removed and newer logs remain fetchable. `LogToRepro` chooses eligible crash logs without repros by build, suppresses logs after a failed attempt, and returns manual repro tasks until they succeed or exhaust explicit failed attempts. Reporting a repro for a different crash title stores the reproduction log on the original bug through `OriginalTitle`.

Dependencies and integration points: uses dashboard API objects from `dashapi`, test context helpers, bug/crash factories from the broader test package, HTTP form helpers, and text serving. It integrates with reporting state because some setup closes, duplicates, or polls bugs before testing repro decisions.

Risks: repro throttling is time-sensitive and depends on constants such as `maxReproPerBug`, `maxReproLogs`, and `reproStalePeriod`. The `MayBeMissing` flag intentionally changes error handling for missing crashes, so API clients rely on that distinction. Manual repro tasks are retried only when `ReproTaskDone` reports failures; silent workers that never call completion keep the task available.

Test signals: passing tests show that the dashboard asks managers for repros only when useful, avoids unbounded failed-log growth, serves repro logs through text links, and handles manual repro task retries without starving or duplicating work.
