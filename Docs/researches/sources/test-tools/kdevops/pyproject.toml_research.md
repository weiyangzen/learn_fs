# sources/test-tools/kdevops/pyproject.toml

Purpose: project-level tool configuration for codespell.

Important APIs/types/functions: `[tool.codespell]` config sets builtins, summary behavior, ignored words `iam,master`, and `write-changes`.

Control flow: no runtime flow; consumed by codespell.

State/persistence behavior: `write-changes` enables codespell to modify files when run with this config.

Dependencies/integration: integrates with developer/CI spell-check tooling.

Risks/test signals: ignored words can hide real typos; write-changes can dirty worktrees. Test signal is successful codespell run with expected ignore list.
