# sources/test-tools/stress-ng/Dockerfile

Purpose: multi-stage Debian 12 container build for a static stress-ng binary and minimal runtime image.

Important APIs and control flow: build stage installs compiler and optional libraries, adds repository as `stress-ng`, regenerates config, performs a static verbose parallel build, strips the binary, installs into `install-root`, then runtime stage copies that root and sets `ENTRYPOINT` to `/usr/bin/stress-ng` with `--help` default.

State and persistence: apt package cache and build outputs are transient to the build stage; installed binary/man/job assets persist in the final image.

Dependencies and integration: integrates with Makefile `Makefile.config`, `STATIC=1`, `DESTDIR` install, and container-image workflows.

Risks and test signals: `ADD .` can include unwanted context files; no apt cache cleanup in build stage is harmless for final size but affects build cache; static build depends on all static libs being available. Signal is an executable final image that prints stress-ng help.
