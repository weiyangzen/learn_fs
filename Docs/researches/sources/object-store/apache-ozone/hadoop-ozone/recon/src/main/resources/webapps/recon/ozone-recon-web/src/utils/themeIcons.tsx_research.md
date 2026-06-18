# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/utils/themeIcons.tsx


Purpose: Shared custom SVG/CSS icons for charts, storage legends, and replication display.

Important APIs/types/functions: Exports `FilledIcon`, `RatisIcon`, `StandaloneIcon`, `ReplicationIcon`, and `GraphLegendIcon`.

Control flow/state/persistence: `ReplicationIcon` chooses RATIS or STAND_ALONE icon by replication type and wraps it in a tooltip with type/factor/leader details. Other icons render SVG or styled letter glyphs.

Dependencies/integration points: Used by storage/quota bars, datanode/pipeline tables, and graph legends. Relies on CSS classes for visual meaning.

Risks/test signals: Unsupported replication types render null. `GraphLegendIcon` has inline SVG and optional height but fixed circle coordinates, so small heights can clip.
