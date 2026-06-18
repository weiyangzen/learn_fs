# sources/test-tools/syzkaller/pkg/email/reply.go

Purpose: `reply.go` creates a quoted email reply body, placing syzbot response text near the relevant `#syz` command when possible.

Important APIs/functions: `FormReply` is the public formatter. `writeReply` inserts blank lines around the response and ensures it ends with a newline.

Control flow and state: `FormReply` scans the original body line by line, prefixes each line with `>` and adds a space unless the original line already starts with `>`. If the message contains exactly one command, the reply is inserted immediately after the first line beginning with `#syz`. If there are multiple commands or no command match, the reply is appended after the quoted body.

Dependencies and integration: it depends on the `Email` struct and `commandPrefix` from `parser.go`. It is used for public bot responses to parsed commands.

Risks: scanner default token limits apply to very long lines. Command attribution is deliberately disabled for multi-command messages. It only checks raw line prefix, so leading whitespace before `#syz` will not trigger inline insertion. Tests in `reply_test.go` cover the major quoting paths.
