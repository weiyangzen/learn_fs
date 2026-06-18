# sources/test-tools/xfstests-bld/config

Purpose: default configuration for root filesystem image builds.

Important APIs and functions: shell variable assignments for `BUILD_ENV`, `SUDO_ENV`, optional `OUT_TAR`, and `gen_image_args`.

Control flow: sourced by `build-appliance`; it does not execute complex logic. Commented examples show schroot-based build environments and tarball output selection.

State and persistence: persists default build policy in the repo. Runtime scripts import these variables into their shell state.

Dependencies and integration: integrates directly with `build-appliance` and `test-appliance/gen-image` argument construction.

Risks: because it is sourced shell, local modifications in `config.custom` or this file can execute arbitrary shell code. Default `SUDO_ENV=sudo` requires passwordless or interactive sudo for image creation.

Test signals: build scripts should pick up networking-enabled `gen_image_args` and default direct build environment when no `config.custom` exists.
