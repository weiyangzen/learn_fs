<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/.devcontainer/setup.sh -->
# sources/security-integrity/cryfs/.devcontainer/setup.sh

**Purpose**
This post-create script orchestrates one-time devcontainer setup.

**Important APIs, Types, And Functions**
It resolves `SCRIPT_DIR` from `BASH_SOURCE[0]` and executes `setup_jj.sh` and `setup_fish.sh`.

**Control Flow**
With `set -e`, the script stops on the first failing setup step. Claude setup is intentionally excluded and runs on container start instead.

**State And Persistence**
It persists whatever the child scripts install: jj tooling/config, fish shell setup, fonts, and aliases.

**Dependencies And Integration Points**
It integrates with `devcontainer.json` as `postCreateCommand`.

**Risks**
A failure in either child script aborts the whole post-create flow. Since the child scripts use network downloads, container creation depends on external availability.

**Test Signals**
A successful devcontainer creation is the main signal; no unit tests exist.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/.devcontainer/setup.sh -->
