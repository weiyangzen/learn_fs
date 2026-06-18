# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/common/SMBException.java

Purpose: `SMBException` is the checked IOException base for SMB-level failures.

Important APIs and control flow: constructors accept message or cause. The static `Wrapper` preserves existing `SMBException` instances and wraps other throwables.

State, dependencies, and integration: used with SMBJ future utilities that require an `ExceptionWrapper`.

Risks: cause-only constructor has no message except the cause string. Tests should verify wrapper idempotency and integration with futures that convert asynchronous errors.
