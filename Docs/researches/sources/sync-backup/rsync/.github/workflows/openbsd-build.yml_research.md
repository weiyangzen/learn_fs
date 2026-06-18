# sources/sync-backup/rsync/.github/workflows/openbsd-build.yml

Purpose: OpenBSD portability CI.

Important APIs/types/functions: VM workflow builds rsync with OpenBSD packages, runs version/tests, includes TCP daemon and `rsync-ssl` smoke where available, and uploads artifacts.

Control flow: path-filtered push/PR and scheduled weekly run. Uses VM action to execute OpenBSD shell commands.

State and persistence: retained artifact bundle.

Dependencies/integration: checks OpenBSD-specific libc/network/filesystem behavior and security defaults.

Risks: OpenBSD package names, VM availability, and stricter platform semantics can break CI independently of source regressions.

Test signals: configure/build/test success and artifact presence.
