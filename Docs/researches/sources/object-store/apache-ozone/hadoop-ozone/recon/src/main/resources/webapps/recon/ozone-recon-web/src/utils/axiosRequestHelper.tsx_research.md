# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/utils/axiosRequestHelper.tsx


Purpose: Utility wrappers for cancellable axios GET/PUT/POST and batch GET requests.

Important APIs/types/functions: Exports `AxiosGetHelper`, `AxiosPutHelper`, `AxiosPostHelper`, `PromiseAllSettledGetHelper`, and `cancelRequests`.

Control flow/state/persistence: Each helper aborts an existing controller if provided, creates a new `AbortController`, and returns the axios request plus controller. Batch helper maps URLs to GET promises and wraps them in `Promise.allSettled`.

Dependencies/integration points: Used by data-heavy legacy/V2 pages that need cancellation during reloads or unmounts.

Risks/test signals: Types use `any` heavily. Aborting an existing request as a side effect can surprise callers if controllers are shared. `cancelRequests` expects an array but does not clear it.
