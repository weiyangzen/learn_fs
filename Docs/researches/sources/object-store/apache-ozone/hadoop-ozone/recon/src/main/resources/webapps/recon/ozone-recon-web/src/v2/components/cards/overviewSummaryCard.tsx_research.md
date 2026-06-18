# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/cards/overviewSummaryCard.tsx


Purpose: V2 generic summary card with optional lead content and a fixed-layout AntD table.

Important APIs/types/functions: `OverviewSummaryCard`, `TableData`, `OverviewTableCardProps`, and `onRow` test id generation.

Control flow/state/persistence: Returns `ErrorCard` when `error` exists. Otherwise builds a title with optional “View Insights” link and state, renders optional `data`, and renders `tableData` with supplied `columns`.

Dependencies/integration points: Used by overview open-key/delete-pending summaries and tested via `overview-${title}-${record.name}` locators.

Risks/test signals: Table row IDs depend on display names, so label changes break tests. `data` can be string or element; callers own formatting.
