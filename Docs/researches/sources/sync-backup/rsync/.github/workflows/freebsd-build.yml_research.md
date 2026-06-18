# sources/sync-backup/rsync/.github/workflows/freebsd-build.yml

Purpose: FreeBSD portability CI.

Important APIs/types/functions: uses a FreeBSD VM action to install build prerequisites, configure with `--with-rrsync`, build, print version, run default and TCP tests, smoke-test `rsync-ssl`, and upload artifacts.

Control flow: Linux-hosted GitHub runner delegates to a FreeBSD VM; commands run inside the VM.

State and persistence: 45-day artifact containing binaries and manpages.

Dependencies/integration: depends on the third-party VM action and FreeBSD package names.

Risks: VM startup/package instability can affect CI. Platform-specific filesystem/ACL behavior may require expected skips.

Test signals: build, `make check`, TCP `runtests.py`, ssl listing smoke, and artifact upload.
