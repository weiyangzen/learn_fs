<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/gcsfuse_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/gcsfuse_test.go

## Purpose

This is the main gcsfuse command integration suite using a canned fake bucket. It validates CLI usage errors, mount preconditions, credential path handling, read/write modes, file/dir modes, uid/gid, implicit and only-dir mounts, foreground behavior, version/help flags, and relative/tilde path expansion for log/key files.

## Important APIs, Types, and Functions

`GcsfuseTest` is an ogletest suite with `gcsfusePath` and temp `dir`. Helpers `gcsfuseCommand`, `runGcsfuseWithEnv`, and `runGcsfuse` execute the built binary with a PATH containing `fusermount`. `createTestFilesForRelativePathTesting` prepares files in cwd and home for path expansion tests.

## Control Flow

Bad usage cases run gcsfuse and match exit errors/output. Mount tests cover nonexistent mount point, mount point as file, missing key file via flag/env, canned contents, read-only write failure, read-write overwrite, custom modes, uid/gid, implicit dirs, only-dir with explicit/implicit/trailing slash paths, relative mount point, foreground process lifecycle, version/help success, and log/key file path variants. Foreground mode reads stderr until a successful mount message, checks the process remains alive, unmounts, and expects clean exit.

## State and Persistence Behavior

The suite creates temp mount directories and temporary key/log path test files. Canned bucket data is in-process fake storage; write tests mutate the mounted view. Mounts are unmounted after each success.

## Dependencies and Integration Points

It depends on `main_test.go` for binary build/fusermount path, `internal/canned` fake bucket data, jacobsa ogletest/matchers, fusetesting directory reads, and `tools/util.Unmount`.

## Risks and Test Signals

Output message regexes and CLI error text are version-sensitive. Path expansion tests use real cwd/home files as dummy key/log files. Passing signal is correct command behavior and mounted canned filesystem semantics across all flag combinations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/gcsfuse_test.go -->
