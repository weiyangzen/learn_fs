## sources/user-network-fs/pyfuse3/.claude/settings.local.json

Purpose: Local Claude tool permission settings for the pyfuse3 repository.

Important APIs/types/functions: JSON grants selected Bash and Serena MCP file operations.

Control flow: Configuration-only; no executable code.

State and persistence: Persists local tool permissions under `.claude`.

Dependencies and integration: Consumed by Claude tooling, not by pyfuse3 runtime/build.

Risks and test signals: Risk is accidental broad tool permission drift. Validate as JSON and keep out of packaging/runtime assumptions.
