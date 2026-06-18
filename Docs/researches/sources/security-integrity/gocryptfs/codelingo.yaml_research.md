# sources/security-integrity/gocryptfs/codelingo.yaml

Purpose: This small configuration file defines CodeLingo/static-review tenets for the gocryptfs repository.

Important APIs and fields: It contains a `tenets` list that points external analysis tooling at selected rule sets.

Control flow and state: It has no runtime control flow. Its only state is analyzer configuration.

Dependencies and integration points: Integrates with CodeLingo or similar code-review automation, not the gocryptfs binary.

Risks and test signals: Stale analyzer config may silently stop running useful checks. Signal is external service recognition and no configuration parse errors.
