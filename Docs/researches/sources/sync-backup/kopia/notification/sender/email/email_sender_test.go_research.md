# sources/sync-backup/kopia/notification/sender/email/email_sender_test.go

Purpose: unit tests for the email provider's SMTP payload construction, option validation, authentication path, and merge semantics.

Important APIs/types/functions: `TestEmailProvider`, `TestEmailProvider_Text`, `TestEmailProvider_AUTH`, `TestEmailProvider_Invalid`, and `TestMergeOptions`. The tests use `go-smtp-mock`, `sender.GetSender`, `email.Options`, `testlogging.Context`, and `require`.

Control flow: the HTML and plain-text tests start a mock SMTP server, create a sender through the registry, send a multiline message with an extra header, wait until the mock receives one message, and compare the exact SMTP request text. The auth test configures username/password against a mock server without AUTH support and asserts the SMTP error. Invalid tests try incomplete option sets and assert wrapped validation messages. Merge tests exercise create and update modes.

State and persistence behavior: state is limited to mock server messages and a mutable destination options struct. No real email is sent.

Dependencies/integration points: validates the sender registry, SMTP formatting, HTML MIME header insertion, default format/port application, and option merge behavior. Risks/test gaps include no test for multiple comma-separated recipients, `CC`, header ordering with more than one map entry, context cancellation, or successful AUTH against an AUTH-capable server. The exact-payload comparisons are strong regression signals for CRLF and header layout.
