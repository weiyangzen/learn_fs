# sources/sync-backup/kopia/notification/sender/sender.go

Purpose: defines the notification sender/provider abstraction and generic registry used by concrete senders.

Important APIs/types/functions: `Provider`, `Sender`, `Factory`, global `allSenders` and `defaultOptions`, `senderWrapper`, `GetSender`, and generic `Register`. A provider sends messages, reports body format support, and summarizes configuration; a sender also exposes a profile name.

Control flow: provider packages call `Register` in `init`, passing typed options and factory functions. `Register` stores a default zero-value options instance and wraps the typed factory in JSON marshal/unmarshal conversion from arbitrary config. `GetSender` looks up the method, invokes the factory, wraps errors, and returns a `senderWrapper` that adds the requested profile name.

State and persistence behavior: registry maps are process-global and mutated during package initialization. No locking is used, so registration is assumed to happen before concurrent use. Persistent config is handled through JSON round-tripping into registered option types.

Dependencies/integration points: central integration point for email, webhook, pushover, testsender, and method config unmarshalling. Risks include runtime panics if registration races, loss of type fidelity through JSON conversion, and unknown-sender errors when provider packages are not imported. Tests are indirect through provider-specific `GetSender` calls and config tests elsewhere.
