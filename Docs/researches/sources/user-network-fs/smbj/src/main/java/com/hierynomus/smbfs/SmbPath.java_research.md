# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/SmbPath.java

Purpose: `smbfs.SmbPath` implements Java NIO `Path` for one `SmbFileSystem`, using backslash separators and a root object to distinguish absolute from relative paths.

Important APIs and control flow: factory methods create root, parsed, and element-backed paths. Name accessors derive file name, parent, subpaths, starts/ends-with, sibling resolution, relativization, iteration, comparison, equality, and string rendering. `resolve` returns the suffix unchanged when absolute, otherwise combines element lists under the current root semantics.

State, dependencies, and integration: immutable fields hold the owning filesystem, root reference, and path elements; `elements == null` means root. Provider methods require this exact path type through `requireSmbPath`.

Risks: `normalize`, `toUri`, `toRealPath`, and watch registration are unimplemented. `differentFileSystem` calls `path.getFileSystem()` before type validation and can throw for non-SMB paths. Case-insensitive `compareTo` may not match `equals`. No dot-dot normalization means SMB calls can receive unresolved segments. Tests should cover root/relative/absolute parsing, separator replacement, element validation, starts/ends edge cases, relativize across roots, and unsupported methods.
