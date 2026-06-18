# sources/security-integrity/ecryptfs-utils/src/desktop/ecryptfs-mount-private.desktop.in

Purpose: desktop launcher metadata for accessing an encrypted private directory.

Important data: translated name/generic name "Access Your Private Data", `Exec=/usr/bin/ecryptfs-mount-private`, `Terminal=true`, application type, System/Security categories, and Ubuntu gettext domain.

Control flow/state: no code; desktop environment launches the command in a terminal.

Dependencies/integration: processed by intltool and installed by desktop Makefile.

Risks: absolute `/usr/bin` path must match package install. Terminal prompt behavior is user-visible.

Test signals: desktop file validation and launcher execution.
