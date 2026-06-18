<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/update_check.go -->
# sources/sync-backup/kopia/cli/update_check.go

## Purpose
Implements optional GitHub update checks, persisted check/notification scheduling, release completeness validation, and update notification logging.

## Important APIs, Types, And Functions
Key symbols are constants for environment and URLs, `updateState`, `updateStateFilename`, `writeUpdateState`, `removeUpdateState`, `getUpdateState`, `maybeInitializeUpdateCheck`, `getLatestReleaseNameFromGitHub`, `verifyGitHubReleaseIsComplete`, `maybeCheckForUpdates`, `maybeCheckGithub`, `maybePrintUpdateNotification`, and `ensureVPrefix`.

## Control Flow
On repository connect/create, initial state may be written or removed. Later repository opens read state, honor `KOPIA_CHECK_FOR_UPDATES=false`, periodically query GitHub latest release, verify checksum signature availability, persist available version, and log a notification when notify interval has elapsed.

## State And Persistence Behavior
Persistent state is `<repo-config>.update-info.json`, written atomically. Network state is GitHub API and release asset availability. No repository data is changed.

## Dependencies And Integration Points
Integrates app config paths, atomic file writes, clock intervals, repo build metadata, semver comparison, HTTP client calls, and environment namespacing.

## Risks And Edge Cases
Network failures are debug-logged and do not block normal use. The code writes next-check time before contacting GitHub to avoid repeated requests. Build versions are normalized with a leading `v`, but unusual version strings may compare unexpectedly.

## Test Signals
Tests should mock HTTP/clock/state files, covering env disable, initial state, due/not-due checks, newer/equal versions, incomplete release checks, and notification throttling.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/update_check.go -->
