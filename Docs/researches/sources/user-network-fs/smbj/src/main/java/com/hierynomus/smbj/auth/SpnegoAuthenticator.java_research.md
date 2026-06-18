# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/SpnegoAuthenticator.java

Purpose: `SpnegoAuthenticator` performs Kerberos/SPNEGO authentication using Java GSS APIs.

Important APIs and control flow: `authenticate` casts to `GSSAuthenticationContext` and executes inside its `Subject`. On first token it creates a `GSSContext` for `cifs@server`, applies mutual-auth and delegation flags, then calls `initSecContext`. It returns a raw SPNEGO token and, when established, queries the Kerberos session key and pads/truncates it to SMB's 16-byte requirement.

State, dependencies, and integration: it stores one `GSSContext` and `GSSContextConfig`. `SMBSessionBuilder` chooses it through the configured factory OID and GSS context type.

Risks: exact class casts mean misuse fails at runtime. `adjustSessionKeyLength` fills to `SIGNATURE_SIZE - 1`, which should be checked for off-by-one padding. Tests should cover multi-token GSS flows with fakes, key length adjustment, config flag application, and GSS exception wrapping.
