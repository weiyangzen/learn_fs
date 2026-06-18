# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/storageBar/storageBar.tsx

Purpose: Renders Ozone datanode storage usage as an Ant Design progress bar with a detailed filesystem/Ozone tooltip.

Important APIs, types, and functions: Exports `StorageBar`. Props combine `DatanodeStorageReport` with optional `showMeta` and `strokeWidth`.

Control flow: Detects whether filesystem-capacity fields are available, computes filesystem used if absent, builds a tooltip table, computes Ozone used percentage from `capacity - remaining`, and colors the bar red above 80 percent.

State and persistence behavior: Pure render component with no React state or persistence.

Dependencies: Uses Ant Design `Progress` and `Tooltip`, `filesize`, local `getCapacityPercent`, and storage-report types.

Integration points: Used by `DatanodesTable` to render each datanode's capacity column.

Risks and edge cases: `reserved` is cast to number when filesystem view exists and may display undefined as a size. Capacity math assumes `remaining` is sane and does not clamp negative/over-100 values itself.

Test signals: Test missing filesystem fields, zero capacity, threshold at 80/81 percent, showMeta text, committed values, and tooltip table contents.
