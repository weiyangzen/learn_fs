# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/upgrade/TestAbstractLayoutVersionManager.java

Purpose: Tests generic `AbstractLayoutVersionManager` initialization, feature finalization, feature allowance, and JMX exposure.

Important APIs/types/functions: `AbstractLayoutVersionManager`, `LayoutFeature`, `init`, `finalized`, `needsFinalization`, `unfinalizedFeatures`, `isAllowed`, metadata/software layout version getters, and MBean attributes.

Control flow: Tests initialize with metadata behind or equal to software layout version, assert failure when metadata version exceeds available features, finalize the next feature, reject out-of-order finalization, verify idempotent already-finalized calls, check feature allowed/disallowed status before and after finalization, and read JMX attributes from the platform MBean server.

State and persistence behavior: Uses in-memory layout feature lists and metadata layout version; registers/closes manager JMX state.

Dependencies and integration points: Uses Mockito spy initialization, JMX `MBeanServer`, and anonymous `LayoutFeature` implementations.

Risks: JMX object names can conflict if managers are not closed or tests run in parallel. The test features return null descriptions, so description handling is not covered.

Test signals: Strong signal for layout version invariants, ordered finalization, allowed-feature gates, and management visibility.
