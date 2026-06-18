# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestOmUpdateEventValidator.java

Purpose: Unit tests for `OmUpdateEventValidator`, which validates that decoded OM update event values match the expected value class for their OM table.

Important APIs and control flow: Setup creates an OM metadata manager and validator from `OMDBDefinition`, then injects a mocked logger. `testValidEvents` checks key, bucket, deleted, prefix, and snapshot tables with correctly typed mock values. `testInvalidEvents` passes strings as values to several tables and expects validation failure plus warning logs.

State and persistence behavior: No durable state. The only mutable global effect is replacing the validator logger through `OmUpdateEventValidator.setLogger`, which test setup controls.

Dependencies and integration points: Uses `OMDBDefinition`, `OMMetadataManager` table names, OM helper classes, Mockito logger capture, and `OMDBUpdateEvent.OMDBUpdateAction.PUT`. It protects downstream Recon tasks from class-cast failures caused by malformed or misdecoded events.

Risks and test signals: Good signal for positive and negative type checks plus log visibility. Risk: static logger replacement can leak if tests are parallelized without isolation.
