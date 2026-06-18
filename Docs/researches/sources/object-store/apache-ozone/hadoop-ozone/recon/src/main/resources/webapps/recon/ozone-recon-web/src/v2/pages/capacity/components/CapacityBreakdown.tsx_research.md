# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/components/CapacityBreakdown.tsx

Purpose: Reusable capacity summary card with statistics and a stacked progress strip.

Important APIs, types, and functions: Exports `CapacityBreakdown`. Props include title, item list, loading flag, and optional error string.

Control flow: If error is present, renders `ErrorCard`; otherwise maps items to AntD `Statistic` values using `filesize`, prefixes colored items with `GraphLegendIcon`, and passes colored items to `StackedProgress`.

State and persistence behavior: Stateless.

Dependencies: Uses AntD Card/Statistic, `filesize`, `GraphLegendIcon`, `ErrorCard`, `StackedProgress`, style constants, and capacity segment type.

Integration points: Used by Capacity and Overview pages for cluster/service capacity cards.

Risks and edge cases: Always formats values as bytes even though item type has an unused `format` property. Negative values are clamped to zero for display. Title React nodes are used in generated keys.

Test signals: Cover loading, error, zero/negative values, colored and uncolored items, stacked-progress inputs, and non-byte formats if implemented.
