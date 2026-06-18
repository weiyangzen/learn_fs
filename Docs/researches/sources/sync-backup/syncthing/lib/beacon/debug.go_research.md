# sources/sync-backup/syncthing/lib/beacon/debug.go

Purpose: Package-level debug logger registration for beacon discovery.

Important APIs/types/functions: Variable `l` is a `slogutil.NewAdapter` registered as "Multicast and broadcast discovery".

Control flow: No functions; initialization occurs at package load.

State and persistence behavior: Registers beacon package description in global slogutil state. No persistence.

Dependencies and integration points: Used by broadcast and multicast implementations for debug logging and package-level log control.

Risks: Global logger side effects occur on import. The description controls API log-level visibility.

Test signals: Indirectly visible through log-level package descriptions.
