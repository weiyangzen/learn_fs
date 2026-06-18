# sources/security-integrity/ecryptfs-utils/src/desktop/Makefile.am

Purpose: builds and installs desktop integration files and the passphrase-record helper script.

Important APIs/targets: installs `ecryptfs-record-passphrase` under ecryptfs-utils data root; transforms `.desktop.in` files into `.desktop` files through intltool; installs desktop entries under the same data root.

Control flow/state: Automake/intltool generate translated desktop files.

Dependencies/integration: configure-generated intltool desktop rule and translation domain.

Risks: install location is application data root, not standard global applications directory, so downstream packaging may move/copy. Desktop entry Exec paths are absolute `/usr/bin`.

Test signals: install tree and intltool generation.
