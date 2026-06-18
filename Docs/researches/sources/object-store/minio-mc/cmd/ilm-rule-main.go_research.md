# Research: sources/object-store/minio-mc/cmd/ilm-rule-main.go

Purpose: registers `mc ilm rule` subcommands.

Important APIs/types/functions: `ilmRuleSubcommands`, `ilmRuleCmd`, and `mainILMRule`.

Control flow: dispatches to add, edit, list, remove, export, and import. Unknown commands route through `commandNotFound`.

State and persistence: none directly.

Dependencies/integration points: child of top-level ILM namespace, fronting lifecycle rule handlers.

Risks: command registration drift can leave handlers unreachable or hidden legacy commands as the only path.

Test signals: command-tree tests should verify full subcommand set.
