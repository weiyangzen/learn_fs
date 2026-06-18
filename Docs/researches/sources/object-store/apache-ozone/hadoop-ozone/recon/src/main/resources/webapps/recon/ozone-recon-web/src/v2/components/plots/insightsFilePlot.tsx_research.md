# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/plots/insightsFilePlot.tsx


Purpose: Bar chart for file size distribution with volume and bucket filters.

Important APIs/types/functions: `FileSizeDistribution`, `handleVolumeChange`, `handleBucketChange`, `updatePlotData`, V2 `MultiSelect`, `FileCountResponse`, and `FilePlotData`.

Control flow/state/persistence: Maintains selected volumes/buckets, bucket option list, bucket select enablement, and sorted file-count map. Volume changes repopulate buckets and selection; plot data filters by selected volumes/buckets, aggregates by file size, sorts ascending, then renders EChart bars. Error state overlays a chart graphic.

Dependencies/integration points: Used by V2 Insights pages and V2 select/chart components.

Risks/test signals: `if (selectedVolumes.length >= 0)` is always true, so empty selected volumes filter out all data. Effects call `updatePlotData` before and after selection updates, causing extra renders.
