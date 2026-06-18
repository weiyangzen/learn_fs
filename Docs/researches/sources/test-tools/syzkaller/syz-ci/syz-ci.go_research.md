# sources/test-tools/syzkaller/syz-ci/syz-ci.go

Purpose: main syz-ci service that auto-updates syzkaller, runs multiple syz-manager instances, handles dashboard jobs, and deprecates assets.

Important APIs/types/functions: `Config`, `ManagerConfig`, `ManagerJobs`, `ManagerJobs.AnyEnabled`, `ManagerJobs.Filter`, `main`, `deprecateAssets`, `uploadSyzkallerBuildError`, `loadConfig`, `loadManagerConfig`, and `inferBaselineConfig`.

Control flow: `main` loads config, handles interrupts, serves HTTP, adjusts GOROOT/PATH, configures updater targets, starts syzkaller updater, creates managers, runs manager loops, starts dashboard job manager when configured, exposes `/upload_cover`, starts asset deprecation worker, and on update/shutdown stops jobs/managers before optionally reexecing. Config loading applies defaults, filters disabled managers, resolves paths, loads partial manager config, auto-assigns ports, applies VM config patches, infers baseline config, and validates managers.

State and persistence: manages directory layout described in file comments: syzkaller latest/current, managers, jobs, workdirs, tags, logs, and assets. Also sets environment for GOROOT/PATH.

Dependencies and integration points: top-level orchestration for updater, manager, job, dashboard, hub, asset storage, and config packages.

Risks: startup validation is intentionally fatal for bad global config. Manager creation failures are tolerated until all fail. Asset storage `IsEmpty` is called even when config may be nil in some paths, depending on method semantics.

Test signals: `config_test.go` loads example config and tests baseline inference; production confidence mainly comes from integration use.
