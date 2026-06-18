<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/.devcontainer/setup_claude.sh -->
# sources/security-integrity/cryfs/.devcontainer/setup_claude.sh

**Purpose**
This post-start script configures Claude Code inside the devcontainer to auto-accept broad tool execution.

**Important APIs, Types, And Functions**
It writes a JSON `PERMISSIONS` object allowing `Bash(*)`, `Edit(*)`, `Write(*)`, `Read(*)`, `WebFetch(*)`, and `NotebookEdit(*)` to `~/.claude/settings.json`, then removes `~/.claude.json`.

**Control Flow**
`set -e` aborts on errors. The script creates the user settings directory, overwrites settings every container start, and clears cached denials.

**State And Persistence**
It mutates user-level Claude configuration in the container home directory, not repository source.

**Dependencies And Integration Points**
It is invoked by devcontainer `postStartCommand` and affects Claude Code behavior in the development environment.

**Risks**
The permission set is intentionally broad and should be limited to trusted container contexts. It overwrites any previous user-level Claude settings in the container.

**Test Signals**
Validation is manual: Claude Code should no longer prompt for the allowed tool categories after container start.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/.devcontainer/setup_claude.sh -->
