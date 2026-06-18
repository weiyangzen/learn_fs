<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicOzFs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicOzFs.java

Purpose: Hadoop `AbstractFileSystem` bridge for the `o3fs` scheme that delegates FileContext-style calls to `BasicOzoneFileSystem`.

Important APIs and functions: constructor `BasicOzFs(URI, Configuration)`, `getUriDefaultPort`, and overridden `finalize`.

Control flow: construction calls `DelegateToFileSystem` with the provided URI, a new `BasicOzoneFileSystem`, the Hadoop configuration, Ozone URI scheme, and authority handling flag `false`. Default port returns `-1` because Ozone FS URIs do not have a required default port. Finalization closes `fsImpl` then delegates to `super.finalize`.

State and persistence behavior: no persistence; state is held by `DelegateToFileSystem` and the wrapped filesystem. Resource cleanup is tied to finalization as a fallback.

Dependencies and integration: Hadoop `DelegateToFileSystem`, `Configuration`, Ozone constants, HDDS audience/stability annotations. Risks include reliance on deprecated/finalization cleanup and constructor-time creation of a concrete basic filesystem. Test signals would come from Hadoop FileContext integration rather than this class directly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicOzFs.java -->
