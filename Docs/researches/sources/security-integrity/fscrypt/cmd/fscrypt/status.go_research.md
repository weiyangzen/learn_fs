# sources/security-integrity/fscrypt/cmd/fscrypt/status.go

## Purpose
Generates global, filesystem, and encrypted-path status output.

## APIs, Types, and Control Flow
`makeTableWriter` builds aligned tables. `encryptionStatus` maps support errors to display text. `policyUnlockedStatus` maps keyring status to `Yes`, `No`, partial, or unknown, including a v1 user-keyring heuristic when a path is available. `writeGlobalStatus` lists relevant filesystems, support status, fscrypt setup status, and totals. `writeOptions` prints protector descriptors, linked status, descriptions, or load errors. `writeFilesystemStatus` prints mount summary, setup mode, protectors, and policies. `writePathStatus` resolves context and policy for a path and prints policy/options/unlocked/protector details.

## State, Dependencies, and Integration
Read-only against mounts, metadata, and keyrings. Integrates with action context/policy/protector options and formatting helpers.

## Risks and Test Signals
Status output is both user-facing and parsed by CLI test helpers, so formatting changes have broad impact. v1 heuristic can report partial state conservatively. CLI status, lock, unlock, and metadata tests exercise this heavily.
