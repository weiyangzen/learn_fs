# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/common/SmbPath.java

Purpose: `smbj.common.SmbPath` is a lightweight UNC path value object distinct from the NIO `smbfs.SmbPath`.

Important APIs and control flow: constructors accept host, share, and optional path, rewriting `/` to `\` and trimming leading UNC separators. Child construction requires a fully specified parent share. `toUncPath` emits `\\host\share\path`, and `parse` splits host/share/path into up to three parts.

State, dependencies, and integration: immutable fields hold hostname, share name, and path. Helpers expose parent, same-host, and same-share checks.

Risks: equality is case-sensitive even though SMB host/share comparisons may be case-insensitive in practice. `getParent` returns itself for share roots. Tests should cover parsing leading slashes, child construction, UNC rendering, parent edge cases, and same-host/share comparisons.
