# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/service/hadoop/FileSystemAccessService.java

## Purpose
`FileSystemAccessService` implements authenticated Hadoop `FileSystem` access for HttpFS. It handles simple or Kerberos login, loads Hadoop configuration, validates target namenodes, creates proxy-user contexts, caches filesystem instances per user, and records instrumentation.

## Important APIs, types, and functions
Config keys include `authentication.type`, Kerberos principal/keytab, filesystem cache purge frequency/timeout, namenode whitelist, and Hadoop config directory. `execute()` validates a service-created configuration and `fs.defaultFS`, runs the executor inside a proxy `UserGroupInformation#doAs`, times the operation, and releases the filesystem. `createFileSystem()` and `releaseFileSystem()` manage unmanaged streaming handles. The nested `CachedFileSystem` tracks a `FileSystem`, active use count, last idle time, and timeout.

## Control flow
Initialization configures Hadoop security, loads `core-site.xml` and `hdfs-site.xml`, forces `fs.hdfs.impl.disable.cache=true`, marks the returned filesystem config with `FileSystemAccessService.created`, clears the server-side umask to `000`, and lowercases the whitelist. Post-init registers unmanaged-FS metrics and schedules periodic purging if timeout is positive.

## State and persistence behavior
State is in-memory: service Hadoop configuration, filesystem template configuration, whitelist, unmanaged count, cache map keyed by short user name, and purge timeout. It reads local Hadoop XML files and uses Hadoop filesystem clients but does not persist service metadata.

## Dependencies and integration points
It depends on Hadoop `Configuration`, `FileSystem`, `UserGroupInformation`, `FsPermission`, `VersionInfo`, `Instrumentation`, and `Scheduler`. It is configured as a default HttpFS service in `httpfs-default.xml` and used by servlet operations and release filters.

## Risks and edge cases
The per-user cache map intentionally retains entries forever; large user cardinality can grow the map. Missing `fs.defaultFS`, non-service-created configs, invalid whitelist authority, Kerberos login failure, or absent Hadoop config directory fail requests or boot. Unmanaged callers must release handles or counts and cached filesystems remain active.

## Test signals
`TestHttpFSMetrics` replaces this service with a subclass that returns a mocked `FileSystem`; its create/append tests verify that `execute()` wraps FS operations and metrics update correctly.
