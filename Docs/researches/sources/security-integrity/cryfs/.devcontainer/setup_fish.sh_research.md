<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/.devcontainer/setup_fish.sh -->
# sources/security-integrity/cryfs/.devcontainer/setup_fish.sh

**Purpose**
This script installs and configures the fish shell experience for the CryFS devcontainer.

**Important APIs, Types, And Functions**
It downloads the Oh My Fish installer with `curl`, runs it with fish, installs `bobthefish`, downloads Hack Nerd Font v3.0.1 with `wget`, extracts it into `~/.local/share/fonts`, and enables nerd font theming.

**Control Flow**
`set -e` and `set -v` make failures fatal and verbose. The script performs network downloads, installation, font extraction, cleanup, and fish universal variable configuration.

**State And Persistence**
It mutates the container user’s fish configuration and local font directory.

**Dependencies And Integration Points**
It depends on fish, curl, wget, tar, GitHub availability, and the devcontainer VS Code terminal font setting.

**Risks**
Network downloads are unpinned by checksum and the script is not idempotent for all Oh My Fish states. Verbose output may expose command details in logs.

**Test Signals**
Opening a fish terminal with the expected theme and font glyphs is the practical validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/.devcontainer/setup_fish.sh -->
