# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/buildtables/buildtables.mk

Makefile for installing and regenerating the PostScript `buildtables` helper.

Key responsibilities:
- Defines platform/install variables for V9-style build.
- Generates executable `buildtables` by substituting path variables into `buildtables.sh`.
- Installs the script and man page.
- Provides `changes` target to rewrite makefile and man page path defaults.

Notable behavior:
- Install steps create target directories and set owner/group/mode.
- Uses legacy `/bin/make` style and shell `sed` substitutions.
