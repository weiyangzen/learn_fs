# sources/security-integrity/ecryptfs-utils/scripts/make.sh

Purpose: interactive legacy installer for building and installing both kernel and userspace eCryptfs components.

Important APIs/commands: prints install locations and mount instructions, warns if not root, waits for ENTER, builds `ecryptfs-kernel`, installs it, then configures/builds/installs `ecryptfs-util --prefix=/usr`.

Control flow/state: changes into fixed sibling directories and runs configure/make/make install. It writes to system directories when run as root.

Dependencies/integration: assumes combined kernel/userspace source layout and a compatible system build environment.

Risks: root install script with no dry-run, hard-coded old paths, and minimal error recovery. Uses bash-style redirection/tests under `/bin/sh`.

Test signals: successful configure/build/install; not suitable as automated unit test.
