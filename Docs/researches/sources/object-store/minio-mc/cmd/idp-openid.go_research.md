# Research: sources/object-store/minio-mc/cmd/idp-openid.go

Purpose: registers the `mc idp openid` command namespace.

Important APIs/types/functions: `idpOpenidSubcommands`, `idpOpenidCmd`, and `mainIDPOpenID`.

Control flow: command dispatches to OpenID config and access-key subcommands, with unknown command fallback.

State and persistence: no direct state changes.

Dependencies/integration points: child of top-level `idp`; includes a TODO for future OpenID policy commands.

Risks: namespace omissions make implemented OpenID operations unreachable. The TODO signals policy parity is not implemented.

Test signals: command registration/help tests.
