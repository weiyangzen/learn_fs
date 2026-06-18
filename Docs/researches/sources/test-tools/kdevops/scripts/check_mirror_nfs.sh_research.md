# sources/test-tools/kdevops/scripts/check_mirror_nfs.sh

Purpose: checks whether a mirror path exists and is mounted as NFS.

Important APIs/types/functions: directory test and `mount | grep -q "on $MIRROR_PATH type nfs"`.

Control flow: prints `n` if path does not exist; otherwise prints `y` only if mount output shows NFS at that path.

State/persistence behavior: read-only.

Dependencies/integration: Kconfig/Make helper for NFS mirror configuration.

Risks/test signals: mount parsing is string-based and path regex is unescaped. Test signal is `y` for NFS-mounted mirror path.
