## sources/security-integrity/attr/autogen.sh

Purpose: bootstrap script for regenerating autotools files.

It updates gettext POTFILES, runs `autopoint --force`, copies Automake's `INSTALL` into `doc/`, and executes `autoreconf -f -i`. State changes are generated autotools files and documentation support files. Dependencies are shell, gettext/autopoint, automake, and autoreconf. Risks are forceful regeneration causing broad metadata churn and dependency-version sensitivity. Test signal is successful configure script generation from a clean checkout.
