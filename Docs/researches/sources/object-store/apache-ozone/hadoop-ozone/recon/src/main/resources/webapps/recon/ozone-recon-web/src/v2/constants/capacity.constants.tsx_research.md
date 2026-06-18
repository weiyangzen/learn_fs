# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/capacity.constants.tsx

Purpose: Provides typed default response objects for capacity and pending-deletion API hooks.

Important APIs, types, and functions: Exports `DEFAULT_CAPACITY_UTILIZATION`, `DEFAULT_SCM_PENDING_DELETION`, `DEFAULT_OM_PENDING_DELETION`, and `DEFAULT_DN_PENDING_DELETION`.

Control flow: No runtime flow; values seed `useApiData` before network responses arrive or after failed requests.

State and persistence behavior: Static defaults only.

Dependencies: Imports capacity response types.

Integration points: Used by the Capacity page to avoid null checks when rendering cluster/service/datanode cards.

Risks and edge cases: Defaults can mask absent API fields as real zero values. The DN default includes a synthetic unknown host that can appear in selectors if not replaced by data.

Test signals: Ensure UI handles defaults without showing misleading unknown hosts after successful empty responses and updates when response fields are added.
