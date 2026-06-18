<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/detect_libvirt_session.sh -->
# sources/test-tools/kdevops/scripts/detect_libvirt_session.sh

Purpose: determines the libvirt URI that kdevops should use, defaulting to `qemu:///system`, switching to `qemu:///session` for distributions detected by libvirt pool helpers, and honoring explicit configuration.

Important APIs and functions: sources sibling `libvirt_pool.sh` and calls `get_pool_vars`, then inspects `USES_QEMU_USER_SESSION` and `CONFIG_LIBVIRT_URI_PATH`.

Control flow: initialize default URI, load helper state, call distribution/pool detection, switch to session when requested, override with configured URI path if non-empty, print final URI.

State and persistence: read-only process state; depends on sourced shell variables from helper scripts and possibly `.config` through those helpers.

Dependencies and integration: `/bin/bash`, `dirname`, and `libvirt_pool.sh`. It is designed for Kconfig or provisioning logic that needs the right libvirt connection string.

Risks: unquoted `dirname $0` and source paths may fail with spaces. `OS_FILE` is assigned but not used directly. Behavior is opaque without `libvirt_pool.sh` side effects. Test signals include stubbing `libvirt_pool.sh` to set `USES_QEMU_USER_SESSION`, testing override behavior, and running under paths with spaces.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/detect_libvirt_session.sh -->
