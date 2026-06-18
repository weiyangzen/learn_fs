# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/common/Check.java

Purpose: `Check` centralizes small assertion helpers.

Important APIs and control flow: `ensureEquals(byte[], byte[], message)` throws `IllegalArgumentException` on byte mismatch; `ensure(condition, message)` throws `IllegalStateException` on false.

State, dependencies, and integration: stateless utility depending only on `Arrays`.

Risks: exception types differ by helper, so callers must match intent. Tests should verify exact exception types and messages for validation paths that use this utility.
