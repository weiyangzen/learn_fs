<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/lustre.conf -->
## sources/user-network-fs/nfs-ganesha/src/config_samples/lustre.conf

Purpose: absolute-minimal sample export for the LUSTRE FSAL.

Important config surface: a single `EXPORT` with `Export_Id = 77`, `Path = /nonexistent`, `Pseudo = /nonexistent`, `Access_Type = RW`, and `FSAL { Name = LUSTRE; }`.

Control flow/state: Ganesha parses this export and dispatches operations through FSAL_LUSTRE. The file has no dynamic behavior and no persistent state of its own; Lustre metadata and data state live in the mounted Lustre filesystem.

Dependencies/integration: requires FSAL_LUSTRE built and runtime Lustre client support. The `Path` must be replaced with a valid Lustre mount path in real deployments. NFSv4 clients use `Pseudo` for namespace construction.

Risks: as written, `/nonexistent` is intentionally placeholder and will not be a useful export. The sample omits client restrictions, security flavor tuning, transports, and protocol restrictions, so production deployments must harden it.

Test signals: after substituting a valid Lustre path, validate daemon config parsing, NFSv4 pseudo path traversal, and basic create/read/remove operations against the Lustre-backed export.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/lustre.conf -->
