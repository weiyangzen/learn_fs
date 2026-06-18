# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/TestStorageContainerServiceProviderImpl.java

Purpose: This compact unit test verifies that `StorageContainerServiceProviderImpl` delegates Recon SCM-facing pipeline APIs to the injected `StorageContainerLocationProtocol` client. It is a wiring and delegation test rather than an SCM integration test.

Important APIs and types: The test uses Guice `Injector`/`AbstractModule`, `StorageContainerServiceProvider`, `StorageContainerServiceProviderImpl`, `StorageContainerLocationProtocol`, `PipelineID`, protobuf `HddsProtos.PipelineID`, `Pipeline`, `ReconUtils`, and `OzoneConfiguration`. Mockito stubs the SCM client, and `@TempDir` supplies the metadata directory configured through `HddsConfigKeys.OZONE_METADATA_DIRS`.

Control flow: `setup` creates a Guice module, mocks the SCM protocol, generates a random pipeline ID, stubs `getPipeline`, and binds the service provider implementation plus dependencies. `testGetPipelines` obtains provider and SCM client instances from the injector, calls `getPipelines`, and verifies `listPipelines` was called once. `testGetPipeline` calls the provider with the saved protobuf ID, asserts a non-null result, and verifies one `getPipeline` invocation.

State and persistence behavior: The only persisted state is the temporary metadata directory configured into `OzoneConfiguration`; no files are inspected. Runtime state is the Guice object graph and the mock invocation history.

Dependencies and integration points: This guards Recon's SPI implementation boundary to SCM. It assumes constructor injection for `StorageContainerServiceProviderImpl` can resolve `StorageContainerLocationProtocol`, `OzoneConfiguration`, and `ReconUtils`, and that the implementation remains a thin delegate for pipeline reads.

Risks: The test does not cover exception propagation, list return values, RPC retries, authentication, or real SCM connectivity. `setup` catches all exceptions and calls `fail()` without preserving diagnostics, so failures can be less informative than necessary.

Test signals: Exact Mockito `times(1)` verification for `listPipelines` and `getPipeline`, plus a non-null returned `Pipeline`.
