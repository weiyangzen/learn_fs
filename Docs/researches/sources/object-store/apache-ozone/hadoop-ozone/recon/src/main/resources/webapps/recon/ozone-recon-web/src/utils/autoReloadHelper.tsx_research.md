# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/utils/autoReloadHelper.tsx


Purpose: Legacy polling helper for pages with auto-refresh.

Important APIs/types/functions: Class `AutoReloadHelper` with `loadData`, `interval`, `initPolling`, `startPolling`, `stopPolling`, and `handleAutoReloadToggle`.

Control flow/state/persistence: `initPolling` calls `loadData` and schedules itself with `window.setTimeout` using `AUTO_RELOAD_INTERVAL_DEFAULT`. Toggle writes `autoReloadEnabled` to `sessionStorage` and starts/stops polling.

Dependencies/integration points: Works with `AutoReloadPanel` callbacks and page-level data loaders.

Risks/test signals: Uses recursive `setTimeout`, not `setInterval`, which is good for drift but requires cleanup on unmount. `stopPolling` does not reset `interval` to 0, and scheduled callbacks can continue if lifecycle cleanup is missed.
