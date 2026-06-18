<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/.devcontainer/devcontainer.json -->
# sources/security-integrity/cryfs/.devcontainer/devcontainer.json

**Purpose**
This file defines a Rust-based VS Code devcontainer for CryFS development.

**Important APIs, Types, And Functions**
It uses `mcr.microsoft.com/devcontainers/rust:1`, adds Rust and GitHub CLI features, installs apt packages `fuse3`, `libfuse3-dev`, and `fish`, runs `.devcontainer/setup.sh` after creation, and `.devcontainer/setup_claude.sh` after each start. VS Code customization sets fish as the default terminal, requests a Hack Nerd Font, and installs DependI, JJK, and Claude Code extensions.

**Control Flow**
Container creation installs features and packages, then setup scripts configure jj and fish. Each start refreshes Claude permissions.

**State And Persistence**
The container stores installed tools, shell configuration, fonts, jj metadata, and user-level Claude settings inside the devcontainer environment.

**Dependencies And Integration Points**
It integrates Docker/devcontainers, VS Code, FUSE/macFUSE-adjacent development dependencies, fish, jj, and Claude Code.

**Risks**
Setup scripts download from the network without pinned hashes. `setup_claude.sh` deliberately grants broad tool permissions in the container. FUSE behavior may still require host capabilities not provided by all container runtimes.

**Test Signals**
Opening the repository in a devcontainer and running Cargo/FUSE tests is the validation path.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/.devcontainer/devcontainer.json -->
