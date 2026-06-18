# sources/test-tools/syzkaller/pkg/email/reply_test.go

Purpose: `reply_test.go` verifies quote formatting and reply insertion for command responses.

Important tests: `TestFormReply` covers insertion after `#syz` commands, alternate command syntaxes, already-quoted input lines, replies with and without trailing newline, appending when no command exists, and appending when multiple commands prevent attribution.

Control flow and state: table fixtures compare exact string output, including blank lines and quote prefixes.

Dependencies and integration: tests use minimal `Email` values and, for the multi-command case, populate `Commands` to force append-only behavior.

Risks/test gaps: no tests cover scanner errors or leading-space command lines. Exact formatting coverage is otherwise strong for intended behavior.
