<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/mountinfo.go -->
# sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/mountinfo.go

Purpose: parser and streaming reader for Linux `/proc/self/mountinfo`, extracting the fields needed by `fuse-abort`.

Important APIs, types, and functions: exports `DefaultPath`, `Open`, `Reader`, `Reader.Next`, `Reader.Close`, and `Mount`. Internal `unescape` decodes backslash-prefixed octal sequences; `parse` extracts major, minor, mountpoint, and filesystem type.

Control flow: `Open` wraps an `os.File` in a scanner. `Next` scans one line, calls `parse`, returns `io.EOF` at end, and propagates parse errors. `parse` splits fields, validates major:minor, skips optional fields until `-`, and unescapes mountpoint/fstype.

State and persistence behavior: state is the open file and scanner cursor only.

Dependencies and integration points: used by `cmd/fuse-abort/main.go`; depends on Linux mountinfo format, `bufio.Scanner`, and octal escaping rules.

Risks and test signals: scanner token limits and strict space splitting can reject unusual lines. Tests and fuzzing cover real entries, escapes, and crashers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/mountinfo.go -->
