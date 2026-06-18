# sources/sync-backup/rsync/.github/workflows/ubuntu-build.yml

Purpose: primary Ubuntu CI and install/uninstall packaging smoke test.

Important APIs/types/functions: installs normal Linux dependencies, configures/builds rsync, runs `make install-all DESTDIR`, verifies expected installed binaries/manpages/stunnel config, runs `make uninstall-all DESTDIR`, checks no files remain, installs system-wide, runs protocol checks and TCP tests, smokes `rsync-ssl`, and uploads artifacts.

Control flow: path-filtered push/PR plus schedule. Uses `sudo` for root-sensitive tests.

State and persistence: temporary DESTDIR removed during smoke; `ubuntu-bin` artifact retained 45 days.

Dependencies/integration: validates Makefile install/uninstall targets as well as runtime suite.

Risks: install path expectations are tied to default configure prefix; runner package churn can affect optional feature coverage.

Test signals: packaging file existence/removal, `make check`, protocol 29/30 checks, TCP daemon tests, ssl smoke, artifact upload.
