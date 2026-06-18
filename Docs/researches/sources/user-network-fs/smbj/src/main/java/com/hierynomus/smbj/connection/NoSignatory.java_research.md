# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/NoSignatory.java

Purpose: `NoSignatory` is the null-object implementation of packet signing.

Important APIs and control flow: `sign` returns the original packet and `verify` always returns true.

State, dependencies, and integration: `Connection` installs it when signing is disabled in config.

Risks: safe only when config/protocol invariants permit unsigned packets. Tests should verify it leaves packets untouched and that SMB3 configs cannot disable signing through `SmbConfig`.
