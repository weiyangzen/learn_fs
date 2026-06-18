# sources/sync-backup/rsync/.github/workflows/netbsd-build.yml

Purpose: NetBSD portability CI.

Important APIs/types/functions: VM-based workflow installs required tools, configures/builds rsync, runs version and tests, and uploads resulting artifacts.

Control flow: scheduled and path-filtered push/PR triggers. Commands run inside a NetBSD VM action from an Ubuntu-hosted job.

State and persistence: retained artifact with binaries/manpages.

Dependencies/integration: validates configure probes and portability code against NetBSD libc, filesystem, and networking.

Risks: third-party VM action and package availability are external failure points; test skips may reflect platform feature gaps.

Test signals: successful configure, make, test suite, TCP smoke where configured, and artifact upload.
