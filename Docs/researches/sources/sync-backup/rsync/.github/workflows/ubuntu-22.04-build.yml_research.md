# sources/sync-backup/rsync/.github/workflows/ubuntu-22.04-build.yml

Purpose: older Ubuntu LTS compatibility coverage.

Important APIs/types/functions: runs on `ubuntu-22.04`, installs ACL/xattr/compression/OpenSSL/doc dependencies, configures with rrsync, builds, installs, checks installed version, runs `make check`, `check30`, `check29`, TCP daemon tests, `rsync-ssl` smoke, and uploads artifacts.

Control flow: scheduled plus path-filtered push/PR. Root-required tests are run with `sudo` and expected skip lists.

State and persistence: `ubuntu-22.04-bin` artifact retained 45 days.

Dependencies/integration: exercises older runner image and protocol compatibility targets.

Risks: expected skip list can go stale as runner capabilities change.

Test signals: install smoke, three protocol test targets, TCP daemon test, SSL smoke, artifacts.
