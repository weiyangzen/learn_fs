# sources/security-integrity/selinux/.circleci/config.yml

Purpose: legacy CircleCI configuration for SELinux userspace static analysis builds.

Important jobs/steps: one `build` job uses `circleci/python:3.6`, installs compiler and SELinux build dependencies, sets `DESTDIR` and `IS_CIRCLE_CI`, downloads refpolicy headers, patches paths for DESTDIR, runs `./scripts/run-scan-build`, and stores scan-build artifacts.

Control flow: checkout, apt dependency install, environment setup, refpolicy bootstrap, static analysis, artifact upload.

State and dependencies: writes `$HOME/destdir`, `/etc/selinux/config`, `/etc/selinux/sepolgen.conf`, and downloaded refpolicy contents. Depends on network access and old CircleCI image availability.

Risks and test signals: dependency/image age and external refpolicy URL stability are risks. Primary signal is clang scan-build artifact generation, not normal CI test coverage.
