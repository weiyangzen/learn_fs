# Research: sources/object-store/minio-mc/cmd/ilm-tier-main.go

Purpose: registers the `mc ilm tier` namespace.

Important APIs/types/functions: `ilmTierSubcommands`, `ilmTierCmd`, and `mainILMTier`.

Control flow: dispatches tier info, list, add, edit, update, verify, check, and remove. Unknown commands route to `commandNotFound`.

State and persistence: no direct state changes.

Dependencies/integration points: child of top-level ILM command and registration point for remote tier management.

Risks: both hidden and visible aliases are present (`edit`/`update`, `verify`/`check`), so changes should preserve intended compatibility.

Test signals: command-tree registration tests.
