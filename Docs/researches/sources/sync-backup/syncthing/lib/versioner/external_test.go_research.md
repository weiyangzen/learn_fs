# sources/sync-backup/syncthing/lib/versioner/external_test.go

Purpose: tests external versioner command failure and success with paths containing spaces/parentheses.

Important tests: `TestExternalNoCommand` prepares a file, runs an invalid command, expects an error, and verifies the file remains. `TestExternal` selects a shell or batch helper command by platform, prepares a nested path with spaces and parentheses, runs `Archive`, and verifies the file is removed. `prepForRemoval` resets and creates the testdata file.

State and persistence: creates and removes local `testdata` under the package directory.

Dependencies and integration: invokes real external script/batch and basic filesystem.

Risks and signals: covers placeholder expansion and command execution at a functional level. It does not test secret environment filtering, symlink panic, restoration unsupported paths, or command stderr wrapping.
