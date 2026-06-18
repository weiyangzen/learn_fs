# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/hooks/useDebounce.tsx

Purpose: Small generic debounce hook for delaying derived values such as search terms.

Important APIs, types, and functions: Exports `useDebounce<T>(value, timeout): T`.

Control flow: Initializes debounced value from input, schedules `setDebounceValue` after the requested timeout whenever value/timeout changes, and clears the timeout on cleanup.

State and persistence behavior: Local debounced value only; no persistence.

Dependencies: Uses React state/effect.

Integration points: Used by table search controls across Buckets, Containers, Datanodes, and Insights.

Risks and edge cases: No special handling for negative/zero timeout beyond native `setTimeout`. Frequent timeout changes reset pending updates.

Test signals: Use fake timers to verify delayed update, cleanup cancelling old timeout, generic object/string values, and timeout changes.
