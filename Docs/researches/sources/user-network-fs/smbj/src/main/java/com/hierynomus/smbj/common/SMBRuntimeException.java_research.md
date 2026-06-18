# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/common/SMBRuntimeException.java

Purpose: `SMBRuntimeException` is the unchecked SMBJ exception wrapper for internal and asynchronous failures.

Important APIs and control flow: constructors accept cause, message, or both. The static `Wrapper` preserves existing runtime exceptions and wraps other throwables.

State, dependencies, and integration: used by promises, IO chunk providers, crypto helpers, and negotiation/session code for failures that cannot be expressed as checked exceptions.

Risks: broad wrapping can obscure original checked exception semantics. Tests should verify wrapper behavior and that critical transport/security failures retain causes.
