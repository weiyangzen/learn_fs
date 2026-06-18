# sources/test-tools/syzkaller/pkg/email/sender/smtp.go

Purpose: `smtp.go` sends plain-text email through SMTP and constructs raw RFC822-style message bytes.

Important APIs/types/functions: `SMTPConfig` holds host, port, credentials, and From address. `NewSMTPSender` returns a `Sender`. `smtpSender.Send` handles message ID generation, envelope validation, TLS or standard SMTP delivery, and returns the message ID. `rawEmail` formats headers and body.

Control flow and state: `Send` generates a UUID-based message ID at the SMTP host, builds the raw message, parses To/Cc addresses for the SMTP envelope, sorts and deduplicates recipients, then either uses implicit TLS for port 465 or `smtp.SendMail` otherwise. The TLS path authenticates, issues MAIL/RCPT/DATA, writes the body, closes the data writer, and quits. `rawEmail` emits From/To/Cc/Subject/In-Reply-To/Message-ID/MIME headers and an 8bit text/plain body.

Dependencies and integration: it uses Go `net/smtp`, `crypto/tls`, `net/mail`, MIME Q encoding, UUIDs, and `slices`. It implements the generic `Sender` contract.

Risks: non-465 ports do not use STARTTLS. Header injection is mitigated for Subject by Q-encoding, but To/Cc display names are written as supplied while envelope parsing rejects invalid recipients. Context is only used for implicit TLS dialing. Tests cover raw formatting and invalid recipient rejection.
