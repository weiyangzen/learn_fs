# sources/sync-backup/kopia/notification/sender/jsonsender/jsonsender.go

Purpose: provides a lightweight notification sender that serializes accepted messages as JSON lines to an `io.Writer`, optionally prefixed for log scanning.

Important APIs/types/functions: `jsonSender`, `Send`, `Summary`, `Format`, `ProfileName`, and `NewJSONSender`. The provider implements `sender.Sender` directly rather than registering as a profile method. It filters by `minSeverity` and encodes `sender.Message` with `encoding/json`.

Control flow: `NewJSONSender` captures prefix, writer, and minimum severity. `Send` returns immediately when `msg.Severity` is below the threshold. Otherwise it writes the prefix to a buffer, JSON-encodes the message with a newline, then writes the whole buffer to the configured writer. `Format` reports plain text because the sender is typically used for machine-readable notification output, not rendered HTML.

State and persistence behavior: no internal durable state is maintained. Persistence depends on the supplied writer; writes are not synchronized, so concurrent callers need an externally safe writer.

Dependencies/integration points: used by notification/reporting code that wants structured output instead of HTTP/SMTP delivery. Risks include partial writer errors being returned without retry, no locking around writes, and the fixed profile name `jsonsender`. The test verifies severity filtering and exact line output.
