# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/storageBar/storageBar.tsx


Purpose: Legacy storage capacity progress bar with tooltip breakdown.

Important APIs/types/functions: `IStorageBarProps`, `StorageBar` class, `filesize.partial`, `getCapacityPercent`, and `FilledIcon`.

Control flow/state/persistence: Computes non-Ozone used as `total - remaining - used`, total used as `total - remaining`, and renders AntD `Progress` with overall percent plus success percent for Ozone used.

Dependencies/integration points: Used by legacy overview and datanode capacity cells.

Risks/test signals: Divide-by-zero in `getCapacityPercent` can produce invalid percent when `total` is zero. Negative non-Ozone values can render if backend fields are inconsistent.
