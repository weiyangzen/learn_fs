<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdCks.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdCks.cc

Purpose: implements `xrdcks`, a local extended-attribute checksum tool for querying, setting, and deleting XRootD checksum metadata on a file.

Important APIs/types/functions: global `xCS` is an `XrdOucXAttr<XrdCksXAttr>` wrapper; `Stat` stores target file metadata; `Display()` prints checksum name/value and marks stale checksums when recorded file mtime differs; `Unable()` formats xattr/stat errors and exits; `Usage()` documents `path cksname [cksval|delete]`; `main()` validates checksum name/value, stats the file, and calls `Get()`, `Set()`, or `Del()`.

Control flow: arguments are checked, the checksum type is validated with `xCS.Attr.Cks.Set(name)`, and the operation is selected from the optional third argument. Query reads the xattr, verifies that the stored checksum type matches the requested type, and displays it. Delete removes the xattr. Set parses a hex value, stamps current file mtime into `fmTime`, clears `csTime`, and writes the xattr.

State/persistence: persists checksum metadata in filesystem extended attributes through `XrdOucXAttr`. It also embeds the file mtime in the xattr so later query can report stale metadata.

Dependencies/integration: integrates `XrdCksXAttr`, `XrdOucXAttr`, POSIX `stat()`, and local filesystem xattr support.

Risks/test signals: query mode appears to have an argument-count defect: after accepting exactly `path cksname`, the code still enters the `else` branch and reads `argv[3]`, which is out of bounds for `argc == 3`. The `strncmp("0x", csVal, 2)` branch also advances non-`0x` strings instead of `0x`-prefixed strings, which looks inverted. Tests should cover query with two operands, delete, set with and without `0x`, invalid checksum names/lengths, stale mtime display, missing xattr, and filesystems without xattr support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdCks.cc -->
