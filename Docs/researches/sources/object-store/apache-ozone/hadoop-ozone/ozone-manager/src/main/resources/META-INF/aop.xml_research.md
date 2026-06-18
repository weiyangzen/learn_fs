<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/resources/META-INF/aop.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/resources/META-INF/aop.xml

Purpose: AspectJ weaving descriptor for OM layout-feature and snapshot-feature enforcement.

Important APIs/types/functions: Registers `OMLayoutFeatureAspect` and `RequireSnapshotFeatureStateAspect`. The weaver includes `org.apache.hadoop.ozone.protocolPB.OzoneManagerRequestHandler` and `OzoneManagerProtocolServerSideTranslatorPB`.

Control flow: At build/runtime weaving time, AspectJ applies advice around annotated methods in the included classes, such as methods marked with `@DisallowedUntilLayoutVersion` or snapshot feature-state annotations.

State and persistence behavior: No runtime state or persistence itself. It affects whether feature-gated methods execute based on OM layout/snapshot state.

Dependencies and integration points: Couples the protocol handler package to upgrade layout and snapshot feature enforcement. Comments note the include list is manually maintained and should include classes with feature annotations.

Risks: If a new annotated class or method is not matched by the include patterns, feature gates may silently not apply. Verbose weave output can affect logs. The manual include list must track refactors.

Test signals: Upgrade/snapshot tests should fail if gated APIs execute before layout finalization or when snapshot feature state disallows them. Build logs can confirm weaving of both protocol classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/resources/META-INF/aop.xml -->
