<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user.go -->
# sources/sync-backup/kopia/cli/command_user.go

## Purpose
Registers the `kopia server users`/`user` command namespace for repository user management.

## Important APIs, Types, And Functions
Defines `commandServerUser` with child commands `add`, `set`, `delete`, `hash`, `info`, and `list`. `setup` creates the parent command and delegates to each child.

## Control Flow
There is no command execution logic in this file. Runtime behavior is handled by the child command implementations after parsing.

## State And Persistence Behavior
No persistent state is changed here; child commands create, update, delete, or list user profile manifests.

## Dependencies And Integration Points
Integrates user-management files under the server command tree and relies on `appServices` repository action plumbing.

## Risks And Edge Cases
Registration drift or alias conflicts are the main risks. The parent description typo (`Manager`) is cosmetic.

## Test Signals
Tests should verify the namespace and aliases expose all child commands and that user operations work through this parent path.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user.go -->
