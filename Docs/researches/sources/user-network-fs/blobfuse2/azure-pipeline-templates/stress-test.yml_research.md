# sources/user-network-fs/blobfuse2/azure-pipeline-templates/stress-test.yml

## Purpose
This template mounts Blobfuse2 and runs the repository stress test suite.

## Important APIs, Types, and Functions
Parameters include `stress_dir`, `idstring`, `parallel`, a step-valued `mountStep`, `quick`, and `distro_name`. It composes `mount.yml`, runs `Go@0 test test/stress_test/stress_test.go`, and cleans up through `cleanup.yml`.

## Control Flow
It mounts using the provided step, runs stress tests with mount path and quick flag under a 120-minute timeout, deletes all files under the mount, prints and clears logs, then unmounts without deleting containers.

## State and Persistence Behavior
It creates stress-test data in the mounted container, clears it with `rm -rf`, and clears `blobfuse2-logs.txt`.

## Dependencies and Integration Points
It is invoked by `verbose-tests.yml` as part of comprehensive storage account testing.

## Risks and Edge Cases
The Go stress test has `continueOnError: true`, so downstream steps can continue after failures. The `stress_dir` and `parallel` parameters are not used by the current commands. Deleting mount contents is broad.

## Test Signals
Signals are Go stress test output, clean file deletion after the run, and logs showing no Blobfuse2 errors.
