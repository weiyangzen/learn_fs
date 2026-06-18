<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/lease/LeaseRecoverer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/lease/LeaseRecoverer.java

Purpose: Implements `ozone admin om lease recover --path=<path>`, recovering the filesystem lease for an Ozone file path through Hadoop `FileSystem` APIs.

Important APIs and types: `FileSystem.get(URI, OzoneConfiguration)`, `LeaseRecoverable`, `Path`, `URI`, Picocli `CommandSpec`, and required `--path` option.

Control flow: `call()` creates a fresh `OzoneConfiguration`, parses the path as a URI, obtains the corresponding `FileSystem`, checks it implements `LeaseRecoverable`, calls `recoverLease(new Path(uri))`, closes the filesystem, and prints success. Unsupported filesystems throw `IllegalArgumentException`.

State and persistence behavior: No local persistence. The remote filesystem/OM lease state is changed by `recoverLease`; whether blocks are closed or client leases are released is delegated to the filesystem implementation.

Dependencies and integration points: Registered below `LeaseSubCommand`; works with `ofs://` or other configured schemes and Hadoop filesystem resolution.

Risks: The command does not use the root admin configuration directly; it constructs a new configuration. It does not check the boolean result because `LeaseRecoverable.recoverLease` here is invoked for side effects. Unsupported schemes fail after opening a filesystem.

Test signals: Exercise OFS/Ozone filesystem lease recovery, unsupported filesystem error, URI parsing, required path option, and success output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/lease/LeaseRecoverer.java -->
