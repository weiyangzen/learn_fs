<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/error_notifications.go -->
# sources/sync-backup/kopia/cli/error_notifications.go

## Purpose
Decides whether repository fatal/error notifications should be sent based on CLI configuration and interactivity.

## Important APIs, Types, And Functions
Defines constants `never`, `always`, and `non-interactive`, plus `App.enableErrorNotifications`.

## Control Flow
The function switches on `c.errorNotifications`: never disables, always enables, non-interactive disables for in-process tests and terminals, otherwise enables.

## State And Persistence Behavior
No persistent state is changed. It reads process stdout terminal status and app flags.

## Dependencies And Integration Points
Depends on `intFd` from `password.go`, `os.Stdout`, and `golang.org/x/term`.

## Risks And Edge Cases
Terminal detection errors fall back to enabling notifications for non-interactive mode. In-process tests are always disabled to avoid unwanted sends.

## Test Signals
Tests should mock or isolate terminal status and verify all three modes plus invalid/default behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/error_notifications.go -->
