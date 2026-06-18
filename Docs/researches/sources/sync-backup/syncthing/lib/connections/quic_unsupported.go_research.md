## sources/sync-backup/syncthing/lib/connections/quic_unsupported.go

Purpose: Registers QUIC schemes as unsupported when built with `noquic`.

Important APIs/types/functions: `errNotInBuild` wraps `errUnsupported`; `init` registers `invalidListener` and `invalidDialer` for `quic`, `quic4`, and `quic6`.

Control flow: At package initialization, QUIC schemes remain recognized but their factories return an unsupported-build error.

State and persistence: Mutates package-global dialer/listener maps. No persistence.

Dependencies and integration points: Depends on build tag `noquic` and invalid factory types elsewhere in the connections package. Integrates with `getDialerFactory` and `getListenerFactory` so config can contain QUIC addresses without panicking.

Risks: Build-tag divergence can hide QUIC regressions from noquic builds and vice versa.

Test signals: Compile-time build coverage only unless noquic tests exercise factory validity paths.
