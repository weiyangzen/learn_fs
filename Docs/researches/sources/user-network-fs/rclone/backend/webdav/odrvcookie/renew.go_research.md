# sources/user-network-fs/rclone/backend/webdav/odrvcookie/renew.go

Purpose: periodic cookie renewal helper for SharePoint WebDAV auth.

Important APIs: `CookieRenew`, `NewRenew`, and `Renew`.

Control flow/state: `NewRenew` starts a ticker and goroutine; `Renew` loops forever, invoking the callback on every tick.

Dependencies/integration: standard `time`; used by `webdav.setQuirks("sharepoint")` to refresh cookies every 12 hours.

Risks/test signals: no stop/cancel path, so short-lived filesystems can leak renewal goroutines. No direct tests.
