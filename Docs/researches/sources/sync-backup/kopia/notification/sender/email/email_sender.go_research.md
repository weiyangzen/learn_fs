# sources/sync-backup/kopia/notification/sender/email/email_sender.go

Purpose: implements the registered `email` notification provider. It turns a `sender.Message` into an SMTP message, optionally authenticates with `smtp.PlainAuth`, adds HTML MIME headers when the configured format is `html`, copies message headers, and sends through `smtp.SendMail`.

Important APIs/types/functions: `ProviderType`, `defaultSMTPPort`, `emailProvider`, `Send`, `Summary`, `Format`, and the package `init` registration with `sender.Register`. `Send` depends on `sender.Message`, `net/smtp`, CRLF header/body joining, and comma-splitting the configured recipient list.

Control flow: construction is indirect through the sender registry. `init` validates `Options`, stores a copy in `emailProvider`, and returns it. A send call builds auth only when `SMTPUsername` is present, assembles mandatory headers, adds MIME headers for HTML bodies, appends message headers, joins with `\r\n`, and calls `smtp.SendMail` with `server:port`, from address, parsed recipients, and payload.

State and persistence behavior: the provider is stateless after construction except for copied options. No message history is retained and no durable state is written. SMTP side effects are external delivery attempts.

Dependencies/integration points: integrates with the notification sender registry, `sender.FormatHTML`, and SMTP servers. Risks include unsorted custom header order, no escaping/sanitization of header values, unused `CC` in delivery, and reliance on `smtp.SendMail` without context cancellation. Test signals come from the email sender tests covering HTML/plain payloads, summary text, auth failure, invalid options, and option merging.
