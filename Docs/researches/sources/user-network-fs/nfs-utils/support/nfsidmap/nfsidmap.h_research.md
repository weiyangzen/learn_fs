# sources/user-network-fs/nfs-utils/support/nfsidmap/nfsidmap.h

Purpose: `nfsidmap.h` is the public libnfsidmap interface for NFSv4 owner/group string mapping, numeric UID/GID mapping, GSS principal mapping, group-list lookup, and debug logging.

Important APIs and types: It defines `NFS4_MAX_DOMAIN_LEN`, `extra_mapping_types`, `extra_mapping_params`, `nfs4_idmap_log_function_t`, and the exported `nfs4_*` functions. The API separates plain `name@domain` mapping from NFSv4 owner/group-owner helpers and has `_ex` variants for extra mapping parameters such as X.509 certificate content.

State, dependencies, and integration: The header depends on system `uid_t`, `gid_t`, and `size_t` types supplied by including code. It is consumed by `libnfsidmap.c`, bundled plugins, idmapd, tests, and ACL/userland NFSv4 callers.

Risks and test signals: There are no include guards in this snapshot, so repeated inclusion relies on build context. ABI stability matters for all prototypes and enum values. Tests should compile standalone consumers and exercise initialization/termination, default-domain lookup, numeric string fallback behavior, GSS group-list sizing, and logging callbacks.
