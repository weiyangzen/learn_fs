# sources/test-tools/syzkaller/pkg/email/sender/sender.go

Purpose: `sender.go` defines the small abstraction shared by concrete email delivery backends.

Important APIs/types/functions: `Email` contains To, Cc, Subject, InReplyTo, Body, and BugID fields. `Sender` defines `Send(context.Context, *Email) (string, error)`, where the string is the produced message ID when the backend can provide it.

Control flow and state: this file has no behavior and no persistence. It is a contract used by SMTP and dashboard senders.

Dependencies and integration: it depends only on `context`. `dashapi.go` and `smtp.go` implement the interface, allowing higher-level code to choose delivery backend without changing message construction.

Risks: the abstraction is intentionally minimal; it does not model attachments, HTML bodies, envelope-specific recipients, or delivery metadata beyond a message ID. There are no direct tests, but concrete sender tests exercise the interface shape.
