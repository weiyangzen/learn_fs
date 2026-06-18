# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/constants/autoReload.constants.tsx


Purpose: Defines the legacy global auto-reload interval.

Important APIs/types/functions: Exports `AUTO_RELOAD_INTERVAL_DEFAULT = 60 * 1000`.

Control flow/state/persistence: None here; `AutoReloadHelper` uses it for recursive polling timeouts.

Dependencies/integration points: Any component using `AutoReloadHelper` inherits a 60 second refresh cadence.

Risks/test signals: No tests assert the interval. Changing it affects page network load and freshness globally.
