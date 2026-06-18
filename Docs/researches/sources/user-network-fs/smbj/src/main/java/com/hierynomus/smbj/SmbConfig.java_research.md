# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/SmbConfig.java

Purpose: `SmbConfig` is the immutable runtime configuration for SMB connections, negotiation, security, authentication, transport, and IO sizing.

Important APIs and control flow: `builder()` establishes defaults: SMB 3.1.1 through 2.0.2 dialects, signing enabled, DFS disabled, direct TCP transport, proxy socket factory, 1 MiB buffers, 60 second operation timeouts, BC security provider, GSS config, NTLM config, and default authenticators. The builder validates non-null components, positive sizes, socket timeout bounds, dialect presence, signing invariants, SMB3 signing restrictions, and encryption requiring SMB3-compatible dialects.

State, dependencies, and integration: config exposes defensive copies for dialects and authenticators. Default authenticators load SPNEGO reflectively outside Android, then add NTLM. Client capabilities are derived from SMB3 support, DFS, and encryption.

Risks: reflective SPNEGO factory failure aborts default config. `Random` and mutable factories are shared by reference. Disabling signing is forbidden for SMB3 dialects but defaults include SMB3, so tests must account for invariant interactions. Test signals include default values, builder copy isolation, capability derivation, authenticator ordering, timeout conversion, and invalid configuration failures.
