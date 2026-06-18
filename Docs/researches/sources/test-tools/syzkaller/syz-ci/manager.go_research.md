# sources/test-tools/syzkaller/syz-ci/manager.go

Purpose: manages one syz-manager instance: kernel polling/building, image validation, manager process lifecycle, dashboard build upload, and artifact/coverage uploads.

Important APIs/types/functions: `Manager`, `ManagerDashapi`, `createManager`, global `buildSem`/`testSem`, `loop`, `archiveCommit`, `pollAndBuild`, `BuildInfo`, `loadBuildInfo`, `checkLatest`, `createBuildInfo`, `build`, `restartManager`, `testImage`, `reportBuildError`, `createTestConfig`, `writeConfig`, `uploadBuild`, `createDashboardBuild`, `pollCommits`, `backportCommits`, `uploadBuildAssets`, `httpGET`, coverage/corpus/bench upload methods, `uploadFile`, `uploadFileHTTPPut`, `Errorf`, and `ManagerConfig.validate`.

Control flow: on loop start, reuses fresh latest image when possible, otherwise polls kernel repo and builds under global semaphore. Builds go to `latest.tmp`, are tagged, smoke-tested, then atomically replace `latest`. Restart links `latest` to `current`, checks out the built commit, uploads build metadata/assets, writes manager config, and starts `ManagerCmd`. Periodic tasks upload coverage, programs with coverage, coverage stats, corpus, and bench data.

State and persistence: persistent per-manager directories under `managers/<name>/`: kernel repo, workdir, `latest`, `current`, logs, bench file, and serialized `tag` build info. External state includes dashboard builds/assets and optional GCS/HTTP uploads.

Dependencies and integration points: integrates `pkg/build`, `pkg/instance`, `pkg/mgrconfig`, `pkg/asset`, `pkg/gcs`, `pkg/cover`, dashboard API, VCS, and target metadata.

Risks: global semaphores serialize expensive work but can delay coverage/jobs. `latest` replacement is only as atomic as remove/rename permits. Old-kernel lag stops fuzzing if builds keep failing. Coverage generation can consume large memory and is serialized through build semaphore.

Test signals: `manager_test.go` covers commit polling and coverage JSONL upload; manager process handling is in `managercmd.go`.
