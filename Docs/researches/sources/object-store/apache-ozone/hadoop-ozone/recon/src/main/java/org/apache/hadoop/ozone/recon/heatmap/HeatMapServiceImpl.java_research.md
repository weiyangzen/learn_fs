## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/heatmap/HeatMapServiceImpl.java

Purpose: concrete heatmap service that loads a configured provider and converts provider metadata into API heatmap responses.

Important APIs/types/functions: constructor builds `HeatMapUtil` and calls `initializeProvider`; `retrieveData` normalizes leading slash and delegates to utility; `doHeatMapHealthCheck` delegates to provider or returns a non-loaded message.

Control flow: provider class name comes from `OZONE_RECON_HEATMAP_PROVIDER_KEY`; utility reflectively loads it; provider is initialized with Ozone config, OM metadata manager, namespace summary manager, and Recon SCM. Failed load/init logs and leaves provider null.

State and persistence: in-memory provider reference and utility; no direct writes. Integrates with pluggable `IHeatMapProvider`, Recon OM metadata, namespace summaries, and SCM.

Risks: provider load failures are swallowed into null provider and normal retrieval returns an empty response. Reflective loading uses default construction. `validatePath` strips only one leading OM key prefix. Tests should cover configured/missing/bad provider, init failure, path normalization, health check fallback, and empty provider response.
