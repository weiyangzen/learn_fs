# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/cards/overviewStorageCard.tsx


Purpose: V2 cluster capacity card with ECharts gauge, usage table, modal explanation, and high-usage highlighting.

Important APIs/types/functions: `OverviewStorageCard`, `getUsagePercentages`, `StorageReport`, `EChart`, and modal/table data for Ozone used, non-Ozone used, remaining, and pre-allocated space.

Control flow/state/persistence: Uses `useMemo` for percentages and `useState` for info modal visibility. Builds gauge series from positive percentage segments, links to `/NamespaceUsage`, and marks card border red above 79% usage.

Dependencies/integration points: Used by V2 Overview and Capacity contexts; tests assert `capacity-*` row IDs and formatted values.

Risks/test signals: Division by zero when capacity is 0 produces NaN/Infinity. This file is duplicated under `v2/components/overviewCard/overviewStorageCard.tsx`, creating maintenance drift risk.
