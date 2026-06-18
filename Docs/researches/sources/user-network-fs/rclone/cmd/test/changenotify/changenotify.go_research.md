<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/changenotify/changenotify.go -->
# sources/user-network-fs/rclone/cmd/test/changenotify/changenotify.go

Source read: complete file, 57 lines, 1593 bytes, sha256 `d70bdc288c0bbcfa8e85241b5880c843bb06da1472b84a137f8924af893c2540`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/test/changenotify/changenotify.go_research.md`.

## Purpose
Defines `rclone test changenotify`, a developer command for logging remote change notifications.

## Important APIs, types, and functions
`pollInterval` flag and `commandDefinition` call the backend `Features().ChangeNotify` callback and then block forever.

## Control flow
The command constructs the Fs, creates a poll channel, starts change notification, sends the poll interval, logs readiness, and waits on an empty select.

## State and persistence behavior
No persistent local state. It may cause backend polling/subscriptions and logs every callback.

## Dependencies and integration points
Depends on test command group, flags, Fs feature detection, and backend change-notify implementations.

## Risks and edge cases
Returns an error if the remote lacks ChangeNotify despite the message naming poll interval. It intentionally runs until interrupted.

## Test signals
Manual diagnostic signal for backend notification support; no unit test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/changenotify/changenotify.go -->
