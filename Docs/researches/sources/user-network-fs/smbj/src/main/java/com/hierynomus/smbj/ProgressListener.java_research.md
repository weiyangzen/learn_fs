# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/ProgressListener.java

Purpose: `ProgressListener` is a minimal callback interface for reporting API progress in bytes.

Important APIs and control flow: implementers receive `onProgressChanged(long numBytes, long totalBytes)`.

State, dependencies, and integration: it is stateless and can be used by transfer operations elsewhere in SMBJ to surface copy/read/write progress.

Risks: no threading, monotonicity, or error contract is specified. Tests should verify callers pass expected byte counts and tolerate listeners that observe total size boundaries.
