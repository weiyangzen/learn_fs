# sources/sync-backup/kopia/notification/sender/testsender/test_sender.go

Purpose: provides a registered in-memory notification provider for tests and internal capture flows.

Important APIs/types/functions: `ProviderType`, context key types, `CaptureMessages`, `CaptureMessagesWithHandler`, `MessagesInContext`, `testSenderProvider`, `Send`, `Summary`, `Format`, and registry `init`.

Control flow: capture helpers attach a `capturedMessages` object to context. The default handler appends message pointers; the custom handler delegates to caller code. `Send` locks the provider mutex, extracts capture state from the context, errors when missing, and calls the handler. Construction validates `Options` and stores them.

State and persistence behavior: captured messages live in the context value and are not durable. The provider has a mutex, but the `capturedMessages.messages` slice itself is protected only when accessed through provider `Send`; external reads via `MessagesInContext` are unsynchronized.

Dependencies/integration points: used by notification tests and code that wants to observe sends without network side effects. Risks include context-key coupling, ignored errors in tests if callers do not assert `Send`, and returning message pointers rather than copies. Tests cover capture and missing-context behavior.
