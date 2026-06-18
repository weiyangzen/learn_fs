## sources/test-tools/syzkaller/pkg/lore-relay/commands.go

Purpose: converts parsed Lore email commands/comments into dashboard external command API requests.

Important APIs/types/functions: `extractCommands`.

Control flow: for each parsed email command, constructs a `dashapi.SendExternalCommandReq` with source/root/message/author/DKIM metadata, maps upstream/reject/unreject commands to specific payloads, and errors on unsupported commands. If no commands but body text exists, creates a comment command.

State and persistence: no state.

Dependencies and integration: depends on `pkg/email`, `pkg/email/lore`, and dashboard `dashapi`; called by relay incoming email handling.

Risks: reject reason uses full email body. Unsupported command causes the whole email to be ignored by caller. Multiple commands are returned but later rejected by relay policy.

Test signals: `commands_test.go` covers command mapping.
