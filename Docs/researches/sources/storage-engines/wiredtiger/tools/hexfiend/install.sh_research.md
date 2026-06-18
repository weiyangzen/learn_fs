# sources/storage-engines/wiredtiger/tools/hexfiend/install.sh

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/hexfiend/install.sh -->
## sources/storage-engines/wiredtiger/tools/hexfiend/install.sh

### Purpose
`install.sh` installs the Hex Fiend application if missing and copies the local `Templates` directory, including `hexparse`, into Hex Fiend's macOS application-support template directory.

### Important APIs, Types, and Functions
The script derives `SRCDIR` from `BASH_SOURCE` and sets `DSTDIR` to `$HOME/Library/Application Support/com.ridiculousfish.HexFiend`. It conditionally invokes `brew install --cask hex-fiend`, creates the destination directory, and copies templates with `cp -a`.

### Control Flow
It checks for `/Applications/Hex Fiend.app`; if absent, it uses Homebrew to install the cask. It then unconditionally copies the source `Templates` directory into the destination and prints guidance for adding `hexparse` to the user's path through copy, symlink, or shell alias.

### State and Persistence
Persistent effects are external to the repository: installation of a macOS app through Homebrew and replacement/copying of template files under the user's home directory. It does not track versions or remove stale templates.

### Dependencies and Integration Points
The script assumes macOS, Homebrew, Bash, and the Hex Fiend bundle/path naming. It integrates directly with `hexparse` because the runner's template search path is hard-coded to the same application-support directory.

### Risks and Test Signals
Unquoted variables in some commands are limited but mostly safe because the main destination is quoted. `cp -a "$SRCDIR/Templates" "$DSTDIR/"` can overwrite existing template files without a diff or backup. CI coverage is unlikely because it requires macOS/Homebrew; a dry-run style test can validate `SRCDIR`/`DSTDIR` derivation and that the copied tree contains `Templates/hexparse`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/hexfiend/install.sh -->
