# sources/sync-backup/kopia/notification/sender/notification_message.go

Purpose: defines the common notification message model and parsing/format validation helpers shared by all senders.

Important APIs/types/functions: `Severity`, `Message`, `ParseMessage`, `Message.ToString`, `FormatPlainText`, `FormatHTML`, and `ValidateMessageFormatAndSetDefault`. `Message` carries subject, optional headers, severity, and body.

Control flow: `ParseMessage` scans header lines until a blank line, special-cases `Subject:`, parses other `key: value` headers, warns and skips malformed header lines, then joins the remaining lines as the body. It errors if no body lines are found and wraps scanner errors. `ToString` writes the subject, sorts header keys for deterministic output, emits a blank line, and appends the body. Format validation accepts `txt` or `html`, fills a provided default when empty, and rejects any other value.

State and persistence behavior: all operations are in-memory. The string representation can be used as a stable serialized template form, but it is not JSON persistence.

Dependencies/integration points: consumed by SMTP, webhook, pushover, JSON, and test senders. Risks include simple colon parsing, no folded/multiline header support, malformed header lines only logging warnings, and format comments elsewhere mentioning markdown even though validation accepts text/html. Tests cover parsing, no-body errors, deterministic string round trip, and format defaults/errors.
