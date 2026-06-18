# sources/user-network-fs/nfs-utils/systemd/60-nfs.rules

Purpose: `60-nfs.rules` applies NFS-related sysctl settings when relevant kernel modules are added.

Important APIs and control flow: udev rules match `ACTION=="add"`, `SUBSYSTEM=="module"`, and module names `sunrpc`, `rpcrdma`, `lockd`, `nfsv4`, and `nfs`. Each rule runs `/sbin/sysctl -q --pattern ... --system` with a regex narrowed to the sysctl namespace supported by that module.

State, dependencies, and integration: It has no persistent state of its own; it causes sysctl state to be loaded from the system configuration stack. It integrates with udev and systemd module loading.

Risks and test signals: The comment says "systctl", but behavior is clear. Incorrect regexes could miss module-specific knobs or apply too broad a set. Tests should load modules in a test VM/container with udev monitoring and confirm expected sysctl patterns are applied without failures.
