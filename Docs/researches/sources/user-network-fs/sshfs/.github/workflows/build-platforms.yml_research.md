# sources/user-network-fs/sshfs/.github/workflows/build-platforms.yml

Purpose: GitHub Actions workflow validating sshfs across platform variants beyond the primary Ubuntu compiler matrix.

Important APIs/types/functions: triggers on push, pull request, and manual dispatch; read-only contents permission; concurrency cancellation; `linux-compat` matrix for Ubuntu latest/22.04/ARM/release/debug/hardened; Alpine musl container build; FreeBSD VM build; artifact upload on test/build failures.

Control flow: Linux jobs install compiler, Meson, FUSE3, GLib, and optionally OpenSSH/FUSE test dependencies, build with Meson/Ninja, configure localhost SSH for test lanes, check `/dev/fuse`, run pytest from build, and upload logs/results. Alpine and FreeBSD jobs perform build-only validation in their environments.

State and persistence behavior: CI artifacts persist test XML and Meson logs.

Dependencies and integration points: pinned GitHub actions, Docker Alpine image digest, `vmactions/freebsd-vm`, Meson build files, and pytest tests.

Risks: FUSE availability on hosted runners can be fragile. Build-only non-Linux lanes may miss runtime bugs. Pinned actions improve repeatability but require maintenance.

Test signals: matrix build success, pytest on Linux lanes, hardened CFLAGS build, musl build, FreeBSD build, and uploaded logs for failures.
