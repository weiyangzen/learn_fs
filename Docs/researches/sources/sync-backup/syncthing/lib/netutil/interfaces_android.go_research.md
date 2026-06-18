## sources/sync-backup/syncthing/lib/netutil/interfaces_android.go

Purpose: Android-specific network interface enumeration using `github.com/wlynxg/anet` instead of Go's standard `net` package.

Important APIs: `Interfaces` returns `anet.Interfaces`; `InterfaceAddrsByInterface` returns `anet.InterfaceAddrsByInterface`.

Control flow and state: simple wrappers with no state.

Dependencies and integration points: used by OS/network utility code that needs reliable interface addresses on Android. Complements `interfaces_other.go`.

Risks: depends on `anet` behavior and Android permissions/platform APIs. Build constraints rely on filename suffix for Android selection.

Test signals: no Android-specific tests in this subset.
