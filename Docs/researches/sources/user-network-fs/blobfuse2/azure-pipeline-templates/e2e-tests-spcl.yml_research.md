# sources/user-network-fs/blobfuse2/azure-pipeline-templates/e2e-tests-spcl.yml

## Purpose
This template generates a specific Blobfuse2 configuration and runs the shared end-to-end test template against it.

## Important APIs, Types, and Functions
Parameters include config template paths, output config, account metadata, `idstring`, `adls`, distro name, quick-test flag, verbose logging, clone flag, and ADLS symlink behavior. It calls `blobfuse2 gen-test-config`, then delegates to `e2e-tests.yml`.

## Control Flow
The template creates a config from `conf_template`, prints it, calls `e2e-tests.yml` with a mount command using that config and `--default-working-dir=$(System.DefaultWorkingDirectory)`, then unmounts via `cleanup.yml`.

## State and Persistence Behavior
It writes the generated config file and uses the normal mount/cache/container state owned by caller variables.

## Dependencies and Integration Points
It is heavily used by `verbose-tests.yml` to test block cache, file cache, LRU, empty-file, direct-IO, and symlink configurations.

## Risks and Edge Cases
It prints generated config. It assumes `WORK_DIR`, `MOUNT_DIR`, `TEMP_DIR`, and `containerName` exist. The default working directory differs from some other templates that use `$(WORK_DIR)`.

## Test Signals
Signals are config generation success, successful E2E Go tests, log artifact publication when requested, and cleanup unmounting after the run.
