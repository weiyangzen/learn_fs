# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/decommissioningSummary/decommissioningSummary.tsx


Purpose: Hover popover showing decommissioning details for a datanode UUID.

Important APIs/types/functions: `DecommissionSummary`, `getDescriptions`, `SummaryData`, `useApiData`, and `showDataFetchError`.

Control flow/state/persistence: Fetches `/api/v1/datanodes/decommission/info/datanode?uuid=${uuid}`. While loading shows `Spin`; on error shows AntD `Result`; when summary data has datanode details, metrics, and containers, renders `Descriptions`.

Dependencies/integration points: Used in V2 datanode table/decommission views. Depends on API hook retry/error behavior and datanode types.

Risks/test signals: Query parameter is not URL-encoded. Typo `DecommisioningSummaryProps` is harmless. Empty data leaves spinner-like content until conditions change, potentially ambiguous.
