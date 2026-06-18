# sources/security-integrity/ecryptfs-utils/src/Makefile.am

Purpose: recursive Automake root for ecryptfs-utils source components.

Important APIs/targets: `SUBDIRS = key_mod libecryptfs utils daemon desktop include pam_ecryptfs libecryptfs-swig`; maintainer-clean removes generated Makefile input.

Control flow/state: build order ensures key modules, library, utilities, daemon, desktop files, headers, PAM module, and SWIG wrapper are included.

Dependencies/integration: subdirectories are conditionally populated by their own Makefiles/configure conditionals.

Risks: unconditional subdirs must be configured even when features are disabled internally. Build order can matter for libraries consumed by utilities/daemon.

Test signals: recursive source build and install.
