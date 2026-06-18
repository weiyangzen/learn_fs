# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/overviewCard/overviewStorageCard.tsx


Purpose: Duplicate V2 cluster capacity card under an older folder name.

Important APIs/types/functions: Same as `v2/components/cards/overviewStorageCard.tsx`: `OverviewStorageCard`, `getUsagePercentages`, info modal, gauge chart, and usage table.

Control flow/state/persistence: Uses `useState` for info modal and `useMemo` for usage percentages, builds gauge data from storage report, and exposes `capacity-*` test IDs.

Dependencies/integration points: Imports from V2 EChart and overview types. The duplicate path may support older imports during refactor.

Risks/test signals: Exact duplication creates maintenance risk; bug fixes must be applied in both places. Same zero-capacity divide risk and chart rendering concerns apply.
