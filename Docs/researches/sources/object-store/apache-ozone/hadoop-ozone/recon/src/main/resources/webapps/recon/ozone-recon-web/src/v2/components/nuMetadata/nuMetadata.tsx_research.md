# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/nuMetadata/nuMetadata.tsx


Purpose: Namespace Usage metadata table that merges namespace summary, quota, and key usage data for a selected path.

Important APIs/types/functions: `NUMetadata`, local response types, `getObjectInfoMapping`, `processMetadata`, `useApiData`, `fetchData`, `removeDuplicatesAndMerge`, and `byteToSize`.

Control flow/state/persistence: Fetches summary and quota in parallel, waits for both to finish and update, then transforms object info, count stats, quota fields, and special KEY usage into table rows. Maintains table state, processing flag, and pagination page; resets page on path change.

Dependencies/integration points: Calls `/api/v1/namespace/summary`, `/api/v1/namespace/quota`, and for keys `/api/v1/namespace/usage?replica=true`. Uses common error notifications.

Risks/test signals: Path is interpolated without URL encoding. KEY branch returns before `finally` resets processing only because `finally` still runs; state may remain stale on some errors. Many response types are local and permissive.
