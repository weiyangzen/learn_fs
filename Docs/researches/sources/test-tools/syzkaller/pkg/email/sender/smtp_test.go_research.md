# sources/test-tools/syzkaller/pkg/email/sender/smtp_test.go

Purpose: `smtp_test.go` validates raw SMTP message construction and recipient validation.

Important tests: `TestRawEmail` checks full header/body output with To, Cc, In-Reply-To, Message-ID, plain subject, subject containing CRLF injection text encoded safely, and a display name containing encoded CRLF-like text. `TestSendInvalidRecipients` verifies `Send` rejects malformed Cc and To addresses before attempting delivery.

Control flow and state: tests instantiate `smtpSender` directly with a fixed From address. `TestSendInvalidRecipients` uses an empty config, relying on recipient validation to fail before network use.

Dependencies and integration: tests exercise `rawEmail`, `mail.ParseAddress` envelope validation inside `Send`, and MIME Q-encoding behavior.

Risks/test gaps: tests do not start an SMTP server, so TLS and `smtp.SendMail` delivery paths are not integration-tested. They also do not verify recipient deduplication. Header construction edge cases are covered well for known injection concerns.
