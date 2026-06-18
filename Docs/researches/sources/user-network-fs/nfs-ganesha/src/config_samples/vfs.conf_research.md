<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/vfs.conf -->
## sources/user-network-fs/nfs-ganesha/src/config_samples/vfs.conf

Purpose: minimal sample export for the generic POSIX VFS FSAL.

Important config surface: a single `EXPORT` with id `77`, `Path = /nonexistent`, `Pseudo = /nonexistent`, RW access, and `FSAL { Name = VFS; }`.

Control flow/state: Ganesha parses the export and delegates operations to FSAL_VFS, which uses the local kernel/filesystem as backing state. The file itself is static configuration.

Dependencies/integration: requires FSAL_VFS support and a real local path substituted for `/nonexistent`. Integrates with local filesystem permissions, export access policy, and NFSv4 pseudo namespace.

Risks: placeholder path makes the sample nonfunctional until edited. Default broad RW access lacks production client, squash, security, and protocol controls.

Test signals: replace the path with a test directory, start Ganesha, mount the pseudo path, and verify local filesystem changes match NFS client operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/vfs.conf -->
