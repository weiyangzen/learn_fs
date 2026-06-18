# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/fs/OzoneManagerFS.java

Purpose: `OzoneManagerFS` is the OM filesystem-view interface for file and directory status, lookup, and listing operations. It extends `IOzoneAcl`, so filesystem objects can also be checked through the common ACL layer.

Important APIs and types: It declares `getFileStatus`, `lookupFile`, and three `listStatus` overloads, with optional client address and `allowPartialPrefixes`. It uses `OmKeyArgs`, `OmKeyInfo`, and `OzoneFileStatus`.

Control flow: The interface defines no implementation. Concrete key managers perform path resolution, bucket layout handling, metadata lookup, and datanode pipeline ordering.

State and persistence behavior: Implementations read from key/file/directory tables and may shape returned key info with block locations. The interface owns no state.

Dependencies and integration points: OFS/Ozone filesystem clients and OM RPC handlers depend on this contract for filesystem-optimized and object-store listings.

Risks and test signals: Listing semantics are subtle across recursive mode, start keys, partial prefixes, bucket layouts, and client-distance pipeline ordering. Tests should cover files vs directories, missing paths, pagination inclusiveness, partial-prefix listing, ACL checks, and FSO vs OBS behavior.
