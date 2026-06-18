## sources/test-tools/syzkaller/syz-cluster/workflow/retest/main.go

`retest-action` reruns previous reproducers/findings against base and patched kernels. Flags specify retest-task JSON, build IDs, session ID, workdir, and test name. It reports running status, builds instance environments, runs a `retest.Runner`, and reports passed or error with cached logs.

`run` reads and decodes `api.RetestTask`, optionally builds a base instance environment when `base_build` is set, always builds a patched environment, completes configs using `fuzzconfig`, and passes both environments plus session/test IDs to `retest.Runner.Run`. Log caching is bounded to 50 KiB/1000 lines.

State persists through `UploadSessionTest` and any downstream retest runner API calls/findings. Integration is with Argo retest template and build artifacts mounted at `/base` and `/patched`. Risks include final status being only passed/error, fatal status reporting on API failure, optional base environment affecting comparison semantics, and no direct tests in this file.
