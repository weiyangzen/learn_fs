# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/cards/overviewHealthCard.tsx


Purpose: V2 overview health card showing healthy/unhealthy state and availability counts.

Important APIs/types/functions: Default export is named internally `OverviewSummaryCard`; props include `title`, `available`, `total`, optional `linkToUrl`, `loading`, and `error`.

Control flow/state/persistence: Returns `ErrorCard` on missing/error values; otherwise computes `available == total` and renders success/warning icon plus `available/total`, with optional “View More” link in title.

Dependencies/integration points: Used by Overview health sections such as datanode/container health. Depends on AntD Card/Grid, icons, and router Link.

Risks/test signals: Imports `HTMLAttributes`, `Table`, and `ColumnType` but does not use them. Equality uses `==` instead of `===`.
