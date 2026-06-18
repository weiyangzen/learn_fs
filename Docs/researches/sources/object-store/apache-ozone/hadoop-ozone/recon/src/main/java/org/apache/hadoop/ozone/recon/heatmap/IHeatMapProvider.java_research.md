## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/heatmap/IHeatMapProvider.java

Purpose: plugin contract for heatmap data providers, allowing Recon to fetch read-access metadata from external systems such as Solr or other indexes.

Important APIs/types/functions: `retrieveData(path, entityType, startDate)` returns flat `EntityMetaData` rows; `init` receives Ozone config, OM metadata, namespace summary manager, and Recon SCM; default `getSolrAddress`; default `doHeatMapHealthCheck`.

Control flow: implementations are reflectively constructed by `HeatMapUtil` and initialized once by `HeatMapServiceImpl`; retrieval is called per request.

State and persistence: interface has no state; implementations may keep external client state. Integration points are heatmap service, Recon metadata managers, SCM, and health endpoints.

Risks: broad `throws Exception` and no explicit lifecycle/close method. Default health check returns healthy even for providers that do not override it. Tests for implementations should cover initialization, external connectivity, path/entity filtering, date handling, and health-check accuracy.
