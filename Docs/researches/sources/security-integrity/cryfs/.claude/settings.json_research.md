<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/.claude/settings.json -->
# sources/security-integrity/cryfs/.claude/settings.json

**Purpose**
This file configures Claude Code behavior for the CryFS repository.

**Important APIs, Types, And Functions**
It enables `alwaysThinkingEnabled` and allows only `Bash(cargo test *)`, `Bash(cargo build *)`, and `Bash(cargo check *)`.

**Control Flow**
Claude Code reads this JSON and restricts tool execution according to the allowed command patterns.

**State And Persistence**
It is persistent repository configuration for AI tooling, not application state.

**Dependencies And Integration Points**
It integrates with Claude Code rather than Cargo or CryFS runtime code.

**Risks**
The repo-level allowlist is narrower than the devcontainer user-level Claude setup, so behavior can differ inside and outside the container. It also allows broad cargo command suffixes but not formatting or lint commands.

**Test Signals**
There are no code tests. Valid JSON parsing and expected Claude Code behavior are the practical signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/.claude/settings.json -->
