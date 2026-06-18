# sources/user-network-fs/gcsfuse/tools/integration_tests/rename_dir_limit/rename_dir_limit_test.go

## Purpose

This is the harness for directory rename-limit integration tests. It configures `--rename-dir-limit=3` scenarios for flat buckets and default behavior for HNS/zonal buckets, then runs tests under static, only-dir, and persistent mounts.

## Important APIs, Types, and Functions

Constants define package test directory names, directory fixture names, rename targets, temp-file prefixes, and only-dir prefix. Package globals store `storageClient` and `ctx`. `TestMain` controls config loading, storage setup, mounted-directory mode, flag-set generation, mount-mode execution, and process exit.

## Control Flow

`TestMain` parses flags, loads or creates `RenameDirLimit` config, initializes environment and storage client, delegates mounted-directory mode if supplied, builds compatible flags, prepares the test bucket directory, then runs static mounting. If successful, it runs only-dir mounting and then persistent mounting.

## State and Persistence Behavior

The harness creates bucket-backed test directories and mutates package globals. Only-dir mounting sets a dedicated prefix. Storage client state is used by sibling tests to detect hierarchical bucket type and skip flat-only limit failures.

## Dependencies and Integration Points

It depends on Cloud Storage, integration `client`, static/only-dir/persistent mounting helpers, setup/test-suite helpers, and sibling rename/move tests. It integrates with e2e mounted-directory scripts that explicitly run rename-dir-limit under several flag combinations.

## Risks and Edge Cases

Compatibility differs by bucket type: flat buckets use explicit rename-dir-limit flags, while HNS/zonal buckets use default config because native hierarchical operations change semantics. Multiple mount modes can leave state that affects later modes if cleanup is incomplete.

## Test Signals

Harness success across all mount modes indicates directory rename and move semantics are stable for configured bucket type. Failures may reflect mount option translation, bucket capability differences, or recursive operation regressions.
