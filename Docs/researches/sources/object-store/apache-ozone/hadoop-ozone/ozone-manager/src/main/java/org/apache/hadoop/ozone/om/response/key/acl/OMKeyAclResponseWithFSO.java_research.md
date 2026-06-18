# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/acl/OMKeyAclResponseWithFSO.java

Purpose: `OMKeyAclResponseWithFSO` persists ACL updates for FSO files or directories.

Important APIs and types: It extends `OMKeyAclResponse`, stores `isDirectory`, volume ID, bucket ID, and converts key info to `OmDirectoryInfo` for directory updates.

Control flow: It builds the FSO path key. Directory ACL updates write directory table rows; file ACL updates write key/file table rows for the FSO layout.

State and persistence behavior: It updates ACL metadata in either directory table or file table.

Dependencies and integration points: It integrates FSO ACL request handling, `OMFileRequest.getDirectoryInfo`, and bucket layout table routing.

Risks and test signals: Tests should cover directory and file ACL branches, path key generation, layout override/inherited layout, and failed response no-op.
