# sources/user-network-fs/rclone/backend/pikpak/api/types_test.go

Purpose: unit-tests PikPak `Link.Valid`, which decides whether cached download links can be reused.

Important APIs/types/functions: `TestLinkValid` table-tests nil links, empty URLs, future and past URL `expire` parameters, precedence of URL expiry over `Expire`, the 10-second safety buffer, fallback to `Expire`, and invalid query expiry.

Control flow: each row runs as a subtest, builds a `Link`, calls `Valid`, and compares the result to the expected boolean.

State and persistence: no persisted state. Test data uses `time.Now()` to produce relative expirations.

Dependencies/integration: depends on `fmt`, `testing`, and `time`. It validates behavior consumed by `Object.Open` via `setMetaDataWithLink`.

Risks/test signals: the near-expiry case could theoretically be timing-sensitive if the test process stalls, but most cases use one-hour margins. It does not cover malformed URLs where parsing fails entirely. The signal is focused coverage for download link cache invalidation.
