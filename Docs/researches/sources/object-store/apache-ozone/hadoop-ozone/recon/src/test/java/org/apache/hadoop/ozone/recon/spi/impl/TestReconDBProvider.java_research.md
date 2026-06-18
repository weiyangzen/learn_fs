# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/spi/impl/TestReconDBProvider.java

## Purpose
Minimal dependency-injection test for `ReconDBProvider`, the provider for Recon's container-key metadata DB store.

## Important APIs, types, and functions
- Creates a Guice injector with `OzoneConfiguration` bound to a temp `OZONE_RECON_DB_DIR`.
- Binds `ReconDBProvider` as a singleton and calls `getDbStore`.

## Control flow
`@BeforeEach` builds the injector and temp DB configuration. `testGet` obtains the provider instance and asserts the DB store is non-null.

## State and persistence behavior
The provider opens or creates a Recon DB store under the configured temp path. The test does not write records; it only verifies construction and store availability.

## Dependencies and integration points
This provider underlies Recon container metadata managers and other SPI implementations that need the Recon DB store.

## Risks and edge cases
Coverage is intentionally narrow. It does not assert DB path, schema/table creation, close behavior, singleton reuse, or failure modes for invalid directories.

## Test signals
The only signal is a non-null `DBStore` from `ReconDBProvider.getDbStore()`.
