# sources/sync-backup/unison/src/props_xattr.c

Purpose: extended-attribute synchronization stubs for Unison across Linux, BSDs, macOS, and Solaris/illumos.

Important APIs: `unison_xattr_set`, `unison_xattr_remove`, `unison_xattr_get`, `unison_xattrs_list`, and `unison_xattr_updates_ctime`. Unsupported platforms raise the registered OCaml exception `XattrNotSupported`.

Control flow: Linux mangles attribute names by stripping `user.` and prefixing non-user namespaces with `!`; other platforms pass names directly. Set/remove/get call platform APIs (`setxattr`, `extattr_*`, `attropen`, etc.), skipping system attributes. Get first queries length, retries up to ten times on Linux/Darwin `ERANGE`, enforces a 32-bit OCaml string limit, and returns binary strings. List builds OCaml `(name, length)` pairs from platform-specific name buffers or Solaris attribute directories.

State/persistence: mutates xattr name/value pairs on files/directories. Solaris xattrs are treated as simplified file-like name/value blobs without synchronizing their own metadata.

Dependencies/integration: Linux xattr namespace semantics, BSD `extattr`, Darwin `sys/xattr.h`, Solaris `attropen`/attribute directories, OCaml named exception registration, and property synchronization code.

Risks: system attribute filtering is conservative and platform-specific; missing a system attribute can cause permission errors or meaningless syncs. Long paths are capped at 32767 bytes for list. Concurrently changing attributes can trigger retry failure. Solaris does not update ctime for xattr changes, affecting scan strategy.

Test signals: xattr set/get/remove/list roundtrips, binary values, changing-size retry behavior, namespace name mangling on Linux, unsupported exception behavior, system-attribute filtering, and `unison_xattr_updates_ctime` platform result.
