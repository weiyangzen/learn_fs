# sources/security-integrity/ecryptfs-utils/src/desktop/ecryptfs-setup-private.desktop.in

Purpose: desktop launcher metadata for setting up an encrypted private directory.

Important data: translated name/generic name "Setup Your Encrypted Private Directory", `Exec=/usr/bin/ecryptfs-setup-private`, `Terminal=true`, Settings/Security categories, and Ubuntu gettext domain.

Control flow/state: no code; launches setup utility in a terminal.

Dependencies/integration: intltool, desktop Makefile, and installed utility path.

Risks: absolute path and terminal interaction must match distro packaging. Setup utility handles sensitive passphrases, so launcher should not suppress terminal prompts.

Test signals: desktop-file validation and manual launcher test.
