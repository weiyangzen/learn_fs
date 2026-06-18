# sources/test-tools/xfstests-bld/Dockerfile

Purpose: builds a Debian-based Docker image containing the xfstests-bld build environment and an installed xfstests test appliance layout.

Important APIs and functions: Docker directives `FROM debian:trixie`, package-installing `RUN`, `LABEL`, `COPY`, build/install `RUN`, `ENTRYPOINT`, and `CMD`.

Control flow: installs build dependencies, copies the repository to `/devel/xfstests-bld`, builds `fstests-bld` with `config.docker`, makes a tarball, extracts it under `/root`, installs test-appliance files, creates `fsgqa`, removes source tree, creates `/results`, and purges some build packages.

State and persistence: final image persists built xfstests files, appliance files, `/entrypoint`, `/root` contents, user `fsgqa`, and `/results`. Apt caches and documentation are removed to reduce size.

Dependencies and integration: integrates top-level repository, `fstests-bld`, and `test-appliance/docker-entrypoint`. Depends on Debian package availability and Docker build context.

Risks: package names and Debian trixie behavior can change. Purging build dependencies may remove tools needed for debugging inside the image. `COPY .` makes image builds sensitive to local untracked files unless `.dockerignore` exists.

Test signals: successful Docker build and default command `-g quick` via `/entrypoint` indicate the packaged appliance can run quick tests.
