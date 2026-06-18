# sources/test-tools/syzkaller/dashboard/app/entities_datastore.go

Purpose: datastore model layer for dashboard entities: managers, manager stats, builds, bugs, crashes, discussions, reporting state, subsystem reports, jobs, text blobs, repro tasks, and emergency stop state.

Important APIs/types/functions: `Manager`, `ManagerStats`, `Build`, `Bug`, `BugReporting`, `Crash`, `Job`, `Text`, `ReproTask`, `SubsystemReport`, `Discussion`, `EmergencyStop`, `JobType`, `BuildType`, `BisectStatus`, `mgrKey`, `buildKey`, `Bug.key`, `bugKeyHash`, `loadManager`, `updateManager`, `loadBuild`, `lastManagerBuild`, `loadBug`, `canonicalBug`, `loadSimilarBugs`, `addCrashReference`, `removeCrashReference`, `dependencyLoader[T]`, and `runInTransaction`.

Control flow: helpers construct deterministic keys, load entities, apply domain transforms, and write through datastore transactions where races matter. `Bug.Load` migrates legacy `Tags.Subsystems` to `Bug.Labels` and backfills `HeadReproLevel`. `Crash.Load` migrates legacy `Reported` state into ref-counted `CrashReference` entries.

State/persistence: App Engine datastore stores root `Manager`, `Build`, `Bug`, `Text`, and related entities; `Crash` and `Job` are children of `Bug`, and `ManagerStats` is a child of `Manager`. Large logs/configs/repros are separate `Text` entities referenced by IDs. Bug state combines lifecycle, repro, reporting, commit, label, tree-test, crash-history, and AI-workflow fields.

Dependencies/integration: depends on `dashapi`, `pkg/hash`, `pkg/subsystem`, App Engine datastore, namespace config helpers, and is consumed by upload, reporting, jobs, graphs, subsystem, UI, and tests.

Risks/test signals: schema migration hooks are delicate; config-key changes can orphan hashed keys; duplicate chains lack explicit cycle protection; transaction retry behavior has a test-emulator workaround. Direct test coverage includes legacy tag migration, with broad indirect coverage from job/reporting/fix/graph/app tests.
