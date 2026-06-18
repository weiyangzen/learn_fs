# sources/sync-backup/git-lfs/tq/verify_test.go

Purpose: tests upload verification behavior.

Important APIs/types/functions: `TestVerifyWithoutAction` and `TestVerifySuccess`.

Control flow: no-action test expects nil. Success test starts an HTTP server, asserts method/path/header/content length/body, configures endpoint auth access, and calls `verifyUpload`.

State and persistence: local HTTP server and atomic call counter only.

Dependencies and integration points: validates `verifyUpload` request construction and auth routing through `lfsapi`.

Risks: does not test non-2xx status handling, retries on errors, or short OIDs.

Test signals: useful positive-path coverage for verify action.
