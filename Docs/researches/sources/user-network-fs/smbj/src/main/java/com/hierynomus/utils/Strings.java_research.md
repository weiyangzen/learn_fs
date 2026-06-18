<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/utils/Strings.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/utils/Strings.java

Purpose: Small string utility class for delimiter splitting/joining, ASCII null-terminated bytes, and nonblank checks.

Important APIs/types/functions: split(String, char), join(List<String>, char), nullTerminatedBytes(String), and isNotBlank(String).

Control flow: split uses indexOf loop preserving empty segments; join appends delimiter between list entries; nullTerminatedBytes allocates length plus one and copies US-ASCII bytes, leaving final zero; isNotBlank trims and checks empty.

State and persistence behavior: Stateless utility.

Dependencies and integration points: SymlinkPathResolver uses split/join for path normalization. SPNEGO and other SMB helpers can use nullTerminatedBytes.

Risks: nullTerminatedBytes allocates by char length, which can mismatch encoded byte length for non-ASCII input; it uses US_ASCII and may replace characters. split does not handle null input. join does not handle null list elements specially.

Test signals: Empty segments in split, leading/trailing delimiter, join roundtrip, ASCII null terminator, non-ASCII nullTerminatedBytes behavior, null input failure, and isNotBlank trim behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/utils/Strings.java -->
