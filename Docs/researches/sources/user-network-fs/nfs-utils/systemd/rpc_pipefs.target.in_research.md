# sources/user-network-fs/nfs-utils/systemd/rpc_pipefs.target.in

Purpose: This template target groups the configured rpc_pipefs mount unit.

Important APIs and control flow: The unit simply `Requires=@_rpc_pipefsmount@` and starts `After=@_rpc_pipefsmount@`, making consumers depend on a target rather than hard-coding the concrete mount unit name.

State, dependencies, and integration: Template substitution supplies the configured mount unit. It is used by rpc.gssd, idmapd, blkmapd, nfsdcld, and generated pipefs units.

Risks and test signals: If substitution does not match the installed mount unit name, all dependent daemons can fail to order correctly. Tests should inspect installed unit files for consistent `_rpc_pipefsmount` replacement and verify target activation mounts rpc_pipefs.
