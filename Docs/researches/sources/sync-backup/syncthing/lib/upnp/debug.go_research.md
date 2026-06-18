# sources/sync-backup/syncthing/lib/upnp/debug.go

Purpose: package logger adapter for UPnP discovery and port mapping.

Important APIs and control flow: initializes `l` with `slogutil.NewAdapter("UPnP discovery and port mapping")`.

State and persistence: logger only.

Dependencies and integration: used by UPnP discovery, SOAP, and IGD service debug logs.

Risks and test signals: no behavior beyond diagnostics.
