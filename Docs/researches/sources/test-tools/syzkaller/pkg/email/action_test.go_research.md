# sources/test-tools/syzkaller/pkg/email/action_test.go

Purpose: `action_test.go` verifies `NewMessageAction` decision branches.

Important tests: `TestMessageActions` covers a plain new thread, replies to report and patch threads, own-email orphan reply ignored, human orphan reply becoming a new thread, and a patch reply to a report becoming a new patch thread.

Control flow and state: the test is table-driven and constructs minimal `Email` and `OldThreadInfo` values. It compares exact `MessageAction` constants for each named scenario.

Dependencies and integration: the test imports `dashapi` to use real discussion-type constants, ensuring compatibility with the lore parser and dashboard state model.

Risks/test gaps: it does not exercise malformed or ambiguous discussion types beyond the main branch cases. It also does not verify interaction with full parsed email headers; those paths are covered in parser and lore tests.
