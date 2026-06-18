<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/paths/SymlinkPathResolver.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/paths/SymlinkPathResolver.java

Purpose: Decorates a PathResolver with SMB2 symbolic-link resolution for CREATE responses that stop on a symlink.

Important APIs/types/functions: statusHandler() treats STATUS_STOPPED_ON_SYMLINK as successful enough for CREATE response processing. resolve(Session, SMB2Packet, SmbPath, ResolveAction) extracts SMB2Error.SymbolicLinkError, computes a substitute target, normalizes dot and dot-dot path segments, and invokes the action with a new SmbPath. resolve(Session, SmbPath, ResolveAction) delegates proactive resolution to the wrapped resolver.

Control flow: On STATUS_STOPPED_ON_SYMLINK, missing symbolic link error data becomes PathResolveException. Absolute symlink data concatenates substitute name and unparsed tail. Relative symlink data replaces the parsed file name portion with substitute name plus unparsed tail. Non-symlink responses delegate to the wrapped resolver.

State and persistence behavior: Holds only wrapped resolver and composed StatusHandler. No caches.

Dependencies and integration points: Uses SMB2Error.SymbolicLinkError, SMB2Functions.unicode for unparsed byte lengths, UTF_16LE decoding, SmbPath, and Strings.split/join. DiskShare relies on it through PathResolver chains.

Risks: UnparsedPathLength is byte-based and must remain aligned with UTF-16LE path encoding. normalizePath mutates path components and can be sensitive to leading empty UNC-style components. Only same-host/share SmbPath is produced; cross-share symlink semantics are not broadened here.

Test signals: Absolute symlink, relative symlink, dot and dot-dot normalization, missing error data, multibyte UTF-16 names, trailing unparsed path, and composition with DFS status handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/paths/SymlinkPathResolver.java -->
