# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/hooks/useAPIData.hook.ts

Purpose: Generic Axios-backed data hook and one-shot request helper for Recon v2 APIs.

Important APIs, types, and functions: Exports `HttpMethod`, `ApiState<T>`, `UseApiDataOptions`, `useApiData<T>`, and `fetchData<T>`.

Control flow: `useApiData` initializes state, optionally fetches GET URLs, cancels prior requests via `AbortController`, sends data as body or params by method, retries network/5xx failures with linear backoff, calls success/error callbacks, and resets to default data on final failure. `fetchData` performs one manual Axios request.

State and persistence behavior: Hook state includes data/loading/error/lastUpdated/success. Refs hold active abort controller, retry count, retry timer, and mounted marker. No browser persistence.

Dependencies: Uses React hooks and Axios.

Integration points: Core fetch primitive for most v2 pages, tables, Assistant health/models, and manual row expansion/export helpers.

Risks and edge cases: Retry branch rejects immediately while a retry is scheduled, so callers may see errors before final retry outcome. The effect depends only on URL and intentionally suppresses exhaustive deps. `mountedRef` can skip initial fetch when URL starts empty then changes depending on flow.

Test signals: Cover initialFetch true/false, URL changes, abort of prior request, GET params, non-GET body, retryable versus non-retryable errors, callbacks, reset/clearError, and unmount cleanup.
