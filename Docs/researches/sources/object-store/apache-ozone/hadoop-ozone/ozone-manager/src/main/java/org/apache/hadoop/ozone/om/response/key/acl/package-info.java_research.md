# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/acl/package-info.java

Purpose: This package documentation identifies the package as containing key ACL response classes.

Important APIs and types: The package includes `OMKeyAclResponse` and `OMKeyAclResponseWithFSO`, which persist ACL changes for keys, files, and directories.

Control flow: Key ACL request handlers produce updated `OmKeyInfo`; these responses route the write to default key table or FSO file/directory tables.

State and persistence behavior: State changes update ACL metadata in key/file/directory rows without changing block data or bucket accounting.

Dependencies and integration points: The package integrates key ACL request handling, `OmKeyResponse`, `OMFileRequest` directory conversion, and cleanup annotations.

Risks and test signals: Tests should cover FSO directory versus file branches, default-layout key ACL persistence, failed response no-op, and bucket layout propagation.
