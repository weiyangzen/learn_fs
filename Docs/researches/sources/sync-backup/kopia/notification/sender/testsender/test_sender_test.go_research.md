# sources/sync-backup/kopia/notification/sender/testsender/test_sender_test.go

Purpose: validates the test sender's context capture behavior.

Important APIs/types/functions: `TestProvider`, `TestProvider_NotConfigured`, `testsender.CaptureMessages`, `testsender.MessagesInContext`, `sender.GetSender`, and `testsender.Options`.

Control flow: `TestProvider` adds capture state to the test context, constructs a `testsender`, sends three message pointers, then asserts the context contains those messages. `TestProvider_NotConfigured` intentionally skips capture setup, sends one message, and asserts no messages are visible in context.

State and persistence behavior: captured state is context-local and in-memory. No durable files or network calls are made.

Dependencies/integration points: exercises registry construction and context-based capture. Risks/test gaps include `TestProvider_NotConfigured` does not assert the `Send` error, so it only verifies absence of captured state, not the explicit `test sender not configured` contract. There is no coverage for custom handlers, handler errors, `Invalid` options, or concurrent sends.
