# sources/test-tools/syzkaller/pkg/email/action.go

Purpose: `action.go` decides how an incoming parsed email should affect dashboard discussion state: ignore, append to an existing thread, or start a new thread.

Important APIs/types/functions: `OldThreadInfo` records the existing dashboard discussion type. `MessageAction` has `ActionIgnore`, `ActionAppend`, and `ActionNewThread`. `NewMessageAction` is the decision function, consuming parsed `Email`, inferred `dashapi.DiscussionType`, and optional old-thread context.

Control flow and state: messages without `InReplyTo` always start new threads. Replies with known prior thread information append unless a patch reply arrives under a different old thread type, in which case it starts a new patch discussion. Replies from own email with no known old thread are ignored because they likely expose a bot response to an unseen private request. Other orphan replies start a visible sub-thread.

Dependencies and integration: this file depends on `dashboard/dashapi` types and the parsed `Email` model from `parser.go`. `lore/parse.go` uses it while walking message trees.

Risks: the logic intentionally encodes product assumptions about syzbot visibility and patch testing. A wrong `msgType` classification can split or merge discussions incorrectly. Tests in `action_test.go` cover all branches.
