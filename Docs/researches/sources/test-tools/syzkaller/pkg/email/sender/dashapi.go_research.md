# sources/test-tools/syzkaller/pkg/email/sender/dashapi.go

Purpose: `sender/dashapi.go` implements the generic email sender interface by delegating delivery to the syzkaller dashboard API.

Important APIs/types/functions: `DashapiConfig` configures dashboard client/address, sender address, context prefix, and subject prefix. `dashapiSender` holds config plus a dashboard client. `NewDashapiSender` constructs the client. `Send` builds a `dashapi.SendEmailReq`.

Control flow and state: `Send` starts from configured `From`. If the item has a `BugID`, it embeds context into the sender local part using `email.AddAddrContext` and `ContextPrefix`. It prefixes the subject, forwards To/Cc/InReplyTo/body, and returns an empty message ID plus any dashboard error.

Dependencies and integration: it depends on `dashboard/dashapi`, `net/mail`, and address-context helpers from `pkg/email`. It implements `sender.Sender` from `sender.go`.

Risks: callers do not receive a real outgoing message ID. Invalid configured From or context insertion errors abort send. Dashboard API errors propagate directly. No local tests cover this file; SMTP sender tests cover only the alternate implementation.
