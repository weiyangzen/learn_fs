# sources/user-network-fs/rclone/backend/zoho/zoho_test.go

Purpose: declares the Zoho WorkDrive integration test entry point. `TestIntegration` delegates to `fstests.Run` with `RemoteName: "TestZoho:"`, `SkipInvalidUTF8: true`, and a nil object typed as `*zoho.Object`.

Control flow and state are intentionally externalized to rclone's shared backend test suite. The test requires a configured live Zoho remote with valid OAuth, region, and workspace root. The `SkipInvalidUTF8` option is a backend-specific signal that the Zoho encoding/API path cannot represent all invalid UTF-8 cases expected by the generic suite. Risks are the same as most live backend tests: failures can reflect provider availability, quota, or account setup rather than code regressions. There are no unit tests here for region setup, token rewriting, upload response decoding, dir-cache behavior, or copy/move rename edge cases.
