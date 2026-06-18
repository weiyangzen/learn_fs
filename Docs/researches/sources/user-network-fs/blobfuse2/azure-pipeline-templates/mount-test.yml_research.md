# sources/user-network-fs/blobfuse2/azure-pipeline-templates/mount-test.yml

## Purpose
This template runs the Go mount test suite against a generated config.

## Important APIs, Types, and Functions
Parameters are `config` and `idstring`. It composes `cleanup.yml`, then runs `Go@0 test` for `test/mount_test/mount_test.go` with working dir, mount path, config file, and build tags.

## Control Flow
It unmounts first, runs the mount test suite with a two-hour timeout and `continueOnError: true`, prints `blobfuse2-logs.txt`, clears logs, then unmounts again.

## State and Persistence Behavior
It uses and clears mount state and logs. It does not delete containers.

## Dependencies and Integration Points
It is used by `verbose-tests.yml` for mount behavior validation after config generation.

## Risks and Edge Cases
`continueOnError: true` can allow later steps to proceed after mount test failures unless the containing pipeline checks task result semantics. Logs are always cleared after printing.

## Test Signals
Signals are Go test results from `test/mount_test`, Blobfuse2 logs, and clean unmount before and after the suite.
