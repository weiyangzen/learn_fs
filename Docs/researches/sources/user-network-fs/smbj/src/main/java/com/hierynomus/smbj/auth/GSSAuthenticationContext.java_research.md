# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/GSSAuthenticationContext.java

Purpose: `GSSAuthenticationContext` extends `AuthenticationContext` for Kerberos/SPNEGO authentication using a JAAS `Subject` and optional `GSSCredential`.

Important APIs and control flow: constructor stores username/domain with an empty password, plus subject and credentials. Getters expose both GSS objects. `toString` identifies the subject rather than password data.

State, dependencies, and integration: `SpnegoAuthenticator.supports` requires this exact class and runs authentication inside `Subject.doAs`.

Risks: subject and credentials are package-private mutable references. Tests should verify SPNEGO selection, subject propagation, and failure when a plain `AuthenticationContext` is offered to SPNEGO.
