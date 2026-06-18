# sources/test-tools/kdevops/playbooks/files/scripts/detect_libvirt_session.sh

Purpose: shell helper that selects the libvirt URI (`qemu:///system` vs `qemu:///session`) appropriate for the current distribution and kdevops configuration.

Important APIs/types/functions: sources sibling `libvirt_pool.sh`, calls `get_pool_vars`, reads variables `USES_QEMU_USER_SESSION` and `CONFIG_LIBVIRT_URI_PATH`, and prints `LIBVIRT_URI`.

Control flow: default to `qemu:///system`, switch to `qemu:///session` for distributions detected as using qemu user sessions, then override with explicit `CONFIG_LIBVIRT_URI_PATH` if set.

State/persistence behavior: no persistent writes; output is consumed by callers as process state/environment configuration.

Dependencies/integration: integrates guestfs/libvirt workflows with distribution detection logic in `libvirt_pool.sh` and generated Kconfig variables.

Risks/test signals: `$0`-based script directory detection can break when sourced rather than executed; unquoted `source` path can misbehave with spaces. Test signals are expected URI on Fedora-like and non-Fedora systems and explicit override precedence.
