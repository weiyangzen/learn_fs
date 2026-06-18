# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/GSSContextConfig.java

Purpose: `GSSContextConfig` carries client-side GSS/SPNEGO context flags used by `SpnegoAuthenticator`.

Important APIs and control flow: `createDefaultConfig()` builds mutual authentication enabled and credential delegation disabled. Builder setters mutate a temporary config, and `build()` returns a defensive copy.

State, dependencies, and integration: it stores only `requestMutualAuth` and `requestCredDeleg`; additional GSS options are noted but not implemented. `SmbConfig` embeds it and passes it to SPNEGO authentication.

Risks: limited GSS controls may prevent configuring replay, sequence, confidentiality, integrity, or lifetime behavior. Tests should verify defaults, builder copy behavior, and that `SpnegoAuthenticator` applies both exposed options to the `GSSContext`.
