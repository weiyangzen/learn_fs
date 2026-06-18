# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/file/package-info.java

Purpose: This package documentation identifies the package as containing file response classes.

Important APIs and types: The package includes directory create, file create, FSO variants, and lease recovery responses, mostly extending key response infrastructure.

Control flow: File requests stage metadata changes, and these responses replay those changes into key/open-key tables for default layouts or directory/open-file/file tables for FSO layouts.

State and persistence behavior: State changes affect parent directory entries, open file/open key entries, committed directory markers, bucket namespace accounting, and lease metadata.

Dependencies and integration points: The package integrates `OMFileRequest` helpers, `OmKeyResponse`, bucket layout routing, and cleanup annotations.

Risks and test signals: Tests should cover FSO versus non-FSO table selection, parent directory creation, bucket quota updates, and no-op existing directory or failed response paths.
