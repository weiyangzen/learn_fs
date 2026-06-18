# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/overview.constants.tsx

Purpose: Provides typed default values for Overview and shared cluster summary responses.

Important APIs, types, and functions: Exports `DEFAULT_CLUSTER_STATE`, `DEFAULT_TASK_STATUS`, `DEFAULT_OPEN_KEYS_SUMMARY`, and `DEFAULT_DELETE_PENDING_KEYS_SUMMARY`.

Control flow: Static defaults seed `useApiData` and summary components before data arrives.

State and persistence behavior: No state.

Dependencies: Imports overview response types.

Integration points: Used by Overview and Containers page cluster-state hook.

Risks and edge cases: Zero defaults can be indistinguishable from an actual empty cluster unless paired with loading/error state. Service IDs default to `N/A`.

Test signals: Verify loading/error states do not present defaults as fresh data and new backend fields are added to defaults.
