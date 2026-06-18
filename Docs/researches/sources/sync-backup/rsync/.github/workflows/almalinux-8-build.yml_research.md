# sources/sync-backup/rsync/.github/workflows/almalinux-8-build.yml

Purpose: CI build and test coverage for AlmaLinux 8/RHEL-family compatibility.

Important APIs/types/functions: scheduled weekly plus push/PR path filters. Runs inside `almalinux:8` container on `ubuntu-latest`, installs EPEL/PowerTools deps, switches Python to 3.9, configures `--with-rrsync`, builds, runs `make check`, runs TCP daemon tests, smoke-tests `rsync-ssl`, and uploads binaries/manpages.

Control flow: checkout needs git installed in the container; test suite is run both default stdio-pipe and real TCP daemon transport.

State and persistence: uploads a 45-day `almalinux-8-bin` artifact.

Dependencies/integration: exercises older glibc/toolchain and packaging dependencies.

Risks: repository availability for EPEL/PowerTools and container package names can break CI independently of rsync.

Test signals: `make check`, TCP `runtests.py`, `rsync --version`, ssl listing smoke, and artifact creation.
