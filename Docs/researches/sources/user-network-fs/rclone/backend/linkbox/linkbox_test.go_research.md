
# sources/user-network-fs/rclone/backend/linkbox/linkbox_test.go

## Purpose
Runs the generic rclone integration suite for Linkbox.

## Important APIs, Types, And Control Flow
`TestIntegration` calls `fstests.Run` with `RemoteName: "TestLinkbox:"`, `NilObject: (*linkbox.Object)(nil)`, and `SkipLeadingDot: true` because Linkbox does not support leading-dot filenames.

## State And Persistence
The test creates remote objects and directories in the configured Linkbox test account and delegates cleanup to `fstests`.

## Dependencies And Integration Points
Depends on a live `TestLinkbox:` remote and generic rclone test behavior. It validates the backend through public `fs.Fs` and `fs.Object` interfaces.

## Risks And Test Signals
Broadly detects API or implementation regressions but is affected by live service behavior. It does not directly isolate the web-token refresh, upload-url, or CDN-download special cases.
