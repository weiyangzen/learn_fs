<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/mem.conf -->
## sources/user-network-fs/nfs-ganesha/src/config_samples/mem.conf

Purpose: sample export for the in-memory `MEM` FSAL used for testing.

Important config surface: `EXPORT` id `1234` maps arbitrary `Path` and `Pseudo` strings to `FSAL { Name = MEM; }` with RW access. A top-level `MEM` block sets `Inode_Size = 1114112` and `UP_Test_Interval = 20`.

Control flow/state: all filesystem state is volatile and owned by FSAL_MEM in process memory. `Inode_Size` sizes the in-memory inode population needed by pyNFS-style tests; `UP_Test_Interval` starts periodic upcall exercise behavior.

Dependencies/integration: requires MEM FSAL support and integrates mainly with test harnesses, NFS protocol validation, and upcall paths rather than a persistent backing filesystem.

Risks: data disappears on daemon restart. The sample uses arbitrary paths and permissive access, so it is inappropriate for production storage. `UP_Test_Interval` can add background behavior that may confuse latency measurements if left enabled unintentionally.

Test signals: use for parser and protocol smoke tests where persistence is not required; verify creates, lookups, and removes survive only for the running process lifetime.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/mem.conf -->
