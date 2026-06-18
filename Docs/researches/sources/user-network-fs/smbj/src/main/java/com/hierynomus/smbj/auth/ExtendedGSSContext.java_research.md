# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/ExtendedGSSContext.java

Purpose: `ExtendedGSSContext` reflectively accesses vendor-specific JGSS extensions to retrieve the Kerberos session key.

Important APIs and control flow: static initialization locates either Sun or IBM `ExtendedGSSContext` and `InquireType`, resolves `KRB5_GET_SESSION_KEY`, and stores the reflective method. `krb5GetSessionKey` invokes it and wraps failures in `TransportException`.

State, dependencies, and integration: it is used by `SpnegoAuthenticator` after GSS context establishment to obtain the SMB session key.

Risks: unsupported JVMs fail class initialization with `IllegalStateException`. Reflective access may break under module restrictions or vendor differences. Tests should isolate supported and unsupported JVM paths, invocation failures, and key extraction behavior.
