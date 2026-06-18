# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/OzoneFileSystemTestUtils.java

Purpose: tiny utility holder for Ozone filesystem integration tests.

Important APIs/types/functions: `setPageSize(ConfigurationTarget, int)` asserts a positive page size, writes `ozone.fs.listing.page.size`, and disables both `o3fs` and `ofs` filesystem caches so future `FileSystem.get` calls observe the new setting.

Control flow: validate input with Ratis `Preconditions`, set the integer config, then set `fs.o3fs.impl.disable.cache` and `fs.ofs.impl.disable.cache`.

State and persistence behavior: no persistent Ozone state. It mutates only the supplied Hadoop/Ozone configuration target.

Dependencies and integration points: uses Ozone URI scheme constants and `OZONE_FS_LISTING_PAGE_SIZE`. It is used by listing tests such as `OzoneFileSystemTestBase.listStatusIteratorOnPageSize`.

Risks: forgetting to disable caches would make page-size tests reuse an old filesystem instance. Passing zero or negative page size is explicitly rejected.

Test signals: useful signal is whether paginated list tests actually run with the configured page size for both O3FS and OFS.
