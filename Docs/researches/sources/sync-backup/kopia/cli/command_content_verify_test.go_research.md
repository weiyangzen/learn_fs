# sources/sync-backup/kopia/cli/command_content_verify_test.go

## Purpose
Test coverage for `command_content_verify` CLI behavior. It exercises command execution through the Kopia test environment and asserts output, repository state, and error handling for none.

## APIs, Types, and Functions
Important APIs include functions/methods `TestContentVerify`.

## Control Flow, State, and Persistence
Control flow registers a namespace or shared helper used by sibling commands, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content indexes, pack blobs, and content metadata, encrypted repository log blobs, temporary test repositories and captured CLI output. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports bytes, os, path/filepath, strings, testing, github.com/stretchr/testify/require, github.com/kopia/kopia/internal/testutil, github.com/kopia/kopia/tests/testenv. It integrates with Kopia repository internals such as kopia/internal/testutil, kopia/tests/testenv plus external packages bytes, os, path/filepath, strings, testing, plus 1 more.

## Risks and Test Signals
Risks and test signals: test signals come from named tests none.
