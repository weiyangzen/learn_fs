## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/heatmap/HeatMapService.java

Purpose: abstract service contract for retrieving entity read-access heatmap data.

Important APIs/types/functions: single abstract `retrieveData(String path, String entityType, String startDate)` returning `EntityReadAccessHeatMapResponse`.

Control flow and state: none in this class. Implementations decide provider lookup, validation, and response construction.

State and persistence: no persistence. Integration point for APIs that need heatmap data without depending on `HeatMapServiceImpl`.

Risks and test signals: broad `throws Exception` pushes error handling to callers. Tests belong on concrete implementations and should validate contract behavior for missing providers and invalid paths.
