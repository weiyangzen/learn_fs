# sources/user-network-fs/blobfuse2/azure-pipeline-templates/e2e-tests.yml

## Purpose
This shared template mounts Blobfuse2 and runs the Go end-to-end test suite against the mounted filesystem.

## Important APIs, Types, and Functions
Parameters include `idstring`, `distro_name`, a step-valued `mountStep`, `adls`, `clone`, `quick_test`, `enable_symlink_adls`, `artifact_name`, and `verbose_log`. It composes `mount.yml`, runs `df`, `pidstat`, and `Go@0 test` under `test/e2e_tests`.

## Control Flow
It mounts using the provided mount step, verifies `df` contains `blobfuse2`, samples CPU usage through `pidstat` and fails if high, then runs `go test -v -timeout=2h ./...` with mount path, ADLS flag, clone flag, temp path, quick-test flag, symlink flag, and distro name. It optionally publishes `blobfuse2-logs.txt`, tails logs on failure, and clears logs always.

## State and Persistence Behavior
It uses the mount/cache paths owned by the caller and clears `blobfuse2-logs.txt` after execution. Optional artifacts persist logs in Azure Pipelines.

## Dependencies and Integration Points
This is the main E2E harness used by `verbose-tests.yml`, proxy tests, release distro tests, and special config templates. It depends on `mount.yml` for cleanup and mount orchestration.

## Risks and Edge Cases
The CPU comparison uses shell string comparison semantics for `[[ $cpu > 5 ]]`, which may misclassify decimal values. Clearing logs can remove debugging context after artifact publication conditions. Test runtime can be long.

## Test Signals
Signals are mount visibility in `df`, low idle CPU after mount, successful Go E2E tests, and log artifacts when verbose logging is enabled.
