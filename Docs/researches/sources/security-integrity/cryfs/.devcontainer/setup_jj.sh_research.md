<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/.devcontainer/setup_jj.sh -->
# sources/security-integrity/cryfs/.devcontainer/setup_jj.sh

**Purpose**
This script installs and configures Jujutsu (`jj`) in the CryFS devcontainer.

**Important APIs, Types, And Functions**
It installs `cargo-binstall` when missing, runs `cargo binstall --no-confirm jj-cli`, writes fish completions and aliases, initializes jj in colocated mode under `/workspaces/cryfs`, tracks `main@origin`, and copies git user name/email into jj config.

**Control Flow**
The script is verbose and fail-fast. It installs tools, writes shell integration files, initializes the repository, then conditionally propagates identity settings.

**State And Persistence**
It mutates user cargo binaries, fish config, repository jj metadata, bookmark tracking, and user jj config.

**Dependencies And Integration Points**
It depends on cargo, cargo-binstall installer network access, jj, fish, git, and the devcontainer path `/workspaces/cryfs`.

**Risks**
The hard-coded workspace path can fail if the container mounts elsewhere. Re-running `jj git init --colocate` may fail or be noisy on already initialized workspaces. Network installers are not checksum-pinned.

**Test Signals**
`jj st` and fish completions/aliases working inside the devcontainer validate the setup.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/.devcontainer/setup_jj.sh -->
