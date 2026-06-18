# sources/test-tools/syzkaller/dashboard/app/asset_storage_test.go

Purpose: integration tests for the asset storage lifecycle in `asset_storage.go`, including email rendering, UI exposure, API listing, and retention/deprecation behavior.

Important tests and helpers: `TestBuildAssetLifetime` uploads build assets, verifies they appear in a first bug report and `NeededAssetsList`, invalidates the bug, and confirms only the HTML coverage report survives after the closed-bug retention period. `TestCoverReportDisplay` verifies manager UI coverage links are absent before upload, then point to the latest coverage report per manager. `TestCoverReportDeprecation` constructs weekly coverage-report upload timelines and asserts that after the two-week embargo only one coverage report per ISO week remains. `TestFreshBuildAssets` confirms latest-build and fresh-asset protection for build assets without crashes. `TestCrashAssetLifetime` verifies multiple crash mount assets, duplicate title numbering, fsck log links/cleanliness flags, and later removal when the bug is no longer relevant.

Control flow under test: each scenario uses `NewCtx`, test API clients, time advancement, `/cron/deprecate_assets`, and `NeededAssetsList`. Email bodies are compared exactly enough to lock report formatting, download asset ordering, title rendering, fsck metadata, and the absence of attachments.

State and persistence behavior: tests exercise datastore-backed `Build`, `Crash`, and `Bug` state, plus blob/text-link storage for crash logs, kernel configs, repro data, and fsck logs. They verify deprecation changes persisted asset URL sets rather than just in-memory report lists.

Dependencies and integration points: uses `dashapi` asset and bug status APIs, `pkg/email.RemoveAddrContext`, the shared `Ctx` test harness, dashboard mail queues, external link helpers, and manager loading through `loadManagers`.

Risks covered: duplicate asset title handling for multi-asset crash reports, stale asset cleanup after bug invalidation, preservation of latest build assets with no crashes, per-manager coverage report selection, and the retention exception for coverage reports. Gaps include no direct concurrent append test and limited coverage of unknown asset type failures.
