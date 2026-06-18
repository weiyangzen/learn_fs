# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/kcs/mock.go

Purpose: mock kernel build implementation used when `logging.MOCK` is enabled.

Important API: `MockRunBuild(repo, gsBucket, gsPath, gsConfig, kConfigOpts, kbuildOpts, arch, testID, buildLog, log) server.ResultType`.

Control flow: read `mock.txt` from the repository directory and map first line `good` to `server.Pass`, `bad` to `server.Fail`, and `undefined` to `server.Error`; any other content panics.

State and dependencies: depends on a local `git.Repository` and `check.ReadLines`. It does not upload kernels or create build artifacts.

Integration points: used by KCS build and bisect code to simulate build/test outcomes without real kernel builds.

Risks and test signals: missing or empty `mock.txt` can panic through `lines[0]`. It is useful for control-flow testing but does not validate `RunBuild`, GCS upload, or build option handling.
