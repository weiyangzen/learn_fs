## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/OzoneManagerServiceProvider.java

Purpose: this SPI abstracts Recon's synchronization and metadata access to Ozone Manager.

Important APIs and types: declares `start`, `stop`, `getOMMetadataManagerInstance`, and `triggerSyncDataFromOMImmediately`. It returns `OMMetadataManager` for local metadata access.

Control flow: implementations own background sync lifecycle and manual sync triggering. The interface exposes only coarse start/stop plus metadata manager access.

State and persistence: no interface state. Implementations update Recon's local OM RocksDB snapshot and derived task state.

Dependencies and integration points: implemented by `OzoneManagerServiceProviderImpl`; bound by the Recon controller module and used by Recon server/API paths that need OM metadata.

Risks and edge cases: no status API is exposed here, so callers can trigger sync but cannot observe detailed progress through the SPI. `stop` throws generic `Exception`, pushing cleanup error handling to callers.

Test signals: implementation tests should cover scheduler lifecycle, immediate trigger behavior, and metadata manager availability.
