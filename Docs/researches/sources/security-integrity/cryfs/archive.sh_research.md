<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/archive.sh -->
# sources/security-integrity/cryfs/archive.sh

**Purpose**
This small release-helper script creates a compressed source archive from the current git HEAD.

**Important APIs, Types, And Functions**
It runs `git archive --format=tar.gz --prefix=cryfs/ HEAD -o cryfs.tar.gz`.

**Control Flow**
The script is fail-fast via `set -e` and directly invokes git archive with a fixed output name.

**State And Persistence**
It writes `cryfs.tar.gz` in the current working directory. It does not modify repository history.

**Dependencies And Integration Points**
It depends on git and the repository being in a valid state. It likely supports manual release packaging.

**Risks**
The output name is fixed and can overwrite an existing archive without prompting. Uncommitted changes are not included because the archive source is `HEAD`.

**Test Signals**
Successful script execution and inspection/extraction of `cryfs.tar.gz` validate behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/archive.sh -->
