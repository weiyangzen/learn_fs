## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/heatmap/HeatMapUtil.java

Purpose: utility that loads heatmap providers and transforms flat entity access metadata into the nested root/volume/bucket/path tree consumed by the UI.

Important APIs/types/functions: `retrieveDataAndGenerateHeatMap`; `generateHeatMap`; `loadHeatMapProvider`; helpers for entity size lookup, bucket/volume insertion, min/max access counts, average access counts, color ratio calculation, and reflective provider loading.

Control flow: provider returns `EntityMetaData` rows. `generateHeatMap` initializes root min count from the first row, splits each path on `/`, looks up entity size through `EntityHandler.getDuResponse`, inserts or updates volume/bucket/prefix nodes, then computes aggregate sizes, min/max ranges, average access counts, and leaf color ratios.

State and persistence: no writes; reads DU/namespace data via `ReconNamespaceSummaryManager`, `ReconOMMetadataManager`, and Recon SCM. Provider loading uses `Class.forName(...).newInstance()`.

Risks: `generateHeatMap` assumes non-empty input; caller currently guards this. `getEntitySize` returns fallback `256L` on unresolved data, which can hide lookup problems. Color ratio divides by entity max count and uses truncation via floor. Reflection API is deprecated and requires no-arg constructor. Tests should cover empty/null metadata at public utility level, duplicate volumes/buckets, volume-only and bucket-only paths, size lookup failures, min/max/color math, and invalid provider class/type.
