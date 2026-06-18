# sources/security-integrity/ecryptfs-utils/autogen.sh

Purpose: bootstraps Autotools and intltool generated files.

Important APIs/functions: runs `autoreconf -i -v -f` and `intltoolize --copy --force` under `sh -e`.

Control flow/state: stops at first failure; writes generated configure/build support files into the working tree.

Dependencies/integration: requires autoreconf and intltoolize; used by Debian `dh_autoreconf`, release scripts, and developers.

Risks: force mode overwrites generated files. Tooling versions affect generated output.

Test signals: success is prerequisite for `./configure` in fresh checkouts.
