# sources/sync-backup/kopia/tests/end_to_end_test/repository_connect_test.go

## Purpose
End-to-end tests for filesystem repository creation/connect behavior, path validation, reconnect tokens, and format key-derivation configuration.

## Important APIs, Types, and Functions
Tests include `TestFilesystemFlat`, `TestFilesystemRequiresAbsolutePaths`, `TestFilesystemSupportsTildeToReferToHome`, `TestReconnect`, `TestReconnectUsingToken`, `TestRepoConnectKeyDerivationAlgorithm`, and `TestRepoConnectBadKeyDerivationAlgorithm`.

## Control Flow
The tests create flat repositories and inspect directory entries, assert relative paths fail, create under `~/`, disconnect/reconnect normally, parse a reconnect command from `repo status -t -s`, iterate supported key-derivation algorithms and verify `kopia.repository.f`, then corrupt that JSON with a bad algorithm and expect connect failure.

## State and Persistence Behavior
Creates real filesystem repositories, client configs, and modifies the format blob JSON directly in the bad-algorithm test.

## Dependencies and Integration Points
Exercises repository filesystem storage options, path expansion/validation, status token output, format JSON, key derivation algorithm support, and reconnect logic.

## Risks
Text parsing of reconnect command is brittle. Home-directory test writes under the real user home but cleans up. Direct JSON mutation bypasses checksums/encryption assumptions for a targeted failure path.

## Test Signals
Confirms flat repos contain no subdirectories, filesystem paths must be absolute except `~` expansion, reconnect commands work, configured key derivation persists, and unknown algorithms are rejected.
