# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/hooks/useAutoReload.hook.tsx

Purpose: Reusable auto-refresh controller that starts/stops timeout-based polling and persists the enabled toggle in sessionStorage.

Important APIs, types, and functions: Exports `useAutoReload(refreshFunction, interval?)` returning `startPolling`, `stopPolling`, `isPolling`, and `handleAutoReloadToggle`.

Control flow: On mount it reads `sessionStorage.autoReloadEnabled` and starts polling unless explicitly false. Poll invokes the latest refresh function immediately and then schedules the next timeout, suppressing duplicate calls within 100ms.

State and persistence behavior: Tracks `isPolling` and interval value; refs hold timeout id, latest refresh function, and last call timestamp. Persists enabled/disabled state in `sessionStorage`.

Dependencies: Uses React hooks and `AUTO_RELOAD_INTERVAL_DEFAULT`.

Integration points: Used by Overview, Buckets, Containers, Datanodes, and Capacity pages with `AutoReloadPanel`.

Risks and edge cases: Uses `clearTimeout` on a numeric ref and browser `window.setTimeout`, so typing assumes DOM. `startPolling` immediately calls refresh, which can duplicate explicit mount fetches. Persisted toggle is global across pages.

Test signals: Cover default-on behavior, persisted false, interval changes, stop cleanup on unmount, duplicate-call guard, and page-specific refresh functions changing over time.
