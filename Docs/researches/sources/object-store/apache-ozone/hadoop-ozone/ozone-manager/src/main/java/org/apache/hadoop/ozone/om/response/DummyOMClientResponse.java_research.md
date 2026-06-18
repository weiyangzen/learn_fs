# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/DummyOMClientResponse.java

Purpose: `DummyOMClientResponse` is a no-op response implementation for paths that need an `OMClientResponse` wrapper but should not write anything to OM metadata.

Important APIs and types: It extends `OMClientResponse`, is annotated with default `@CleanupTableInfo`, and implements `addToDBBatch` as an empty method.

Control flow: `checkAndUpdateDB` inherited from the base class can call the no-op batch method on OK responses, making this safe where no persistence is expected.

State and persistence behavior: It stores only the `OMResponse`; no DB or cache state is changed.

Dependencies and integration points: It participates in normal response handling without special casing.

Risks and test signals: Tests should assert no batch writes occur and that using it for mutating operations would be a bug because cleanup metadata is empty.
