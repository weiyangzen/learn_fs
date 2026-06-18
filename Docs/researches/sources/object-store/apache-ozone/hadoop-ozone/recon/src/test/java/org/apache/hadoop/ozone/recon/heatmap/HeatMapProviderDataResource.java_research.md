# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/heatmap/HeatMapProviderDataResource.java

Purpose: This resource DTO encapsulates the `buckets` array from Solr/Ranger audit facet JSON for heatmap tests. It maps JSON property `buckets` to an array of `EntityMetaData` objects and protects the internal array with defensive copies.

Important APIs/types/functions: The class uses Jackson `@JsonProperty("buckets")`, `EntityMetaData[]`, `getMetaDataList`, `setMetaDataList`, and `Arrays.copyOfRange`.

Control flow: Jackson deserializes a `resources` JSON node into this type by calling the setter. Consumers call `getMetaDataList`, which returns a copied array when metadata exists or `null` otherwise. The setter copies the entire incoming array into the private field.

State and persistence behavior: The only state is the private `metaDataList` array. There is no persistence. The defensive-copy behavior prevents callers from mutating internal state via the returned array reference, though individual `EntityMetaData` objects remain shared.

Dependencies and integration points: It is used by `TestHeatMapInfo` to transform Solr facet responses into `List<EntityMetaData>` inputs for `HeatMapUtil.generateHeatMap`. It couples the test JSON shape to the Recon API type used by heatmap generation.

Risks: `setMetaDataList` does not handle null input and would throw `NullPointerException` if Jackson supplied null. Defensive copy is shallow, so metadata objects themselves are mutable if the type exposes mutators. The class lives under test sources but models an external JSON shape that must remain aligned with audit provider responses.

Test signals: No direct tests in this file. Indirect signals come from `TestHeatMapInfo`, where `JsonTestUtils.treeToValue` populates the DTO from `resources.buckets` and heatmap generation uses the returned metadata list.
