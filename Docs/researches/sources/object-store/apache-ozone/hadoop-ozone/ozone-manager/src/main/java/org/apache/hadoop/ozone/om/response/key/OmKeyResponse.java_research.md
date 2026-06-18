# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OmKeyResponse.java

Purpose: `OmKeyResponse` is the key-response base class that stores the bucket layout used by key/file table operations.

Important APIs and types: It extends `OMClientResponse`, has constructors with explicit `BucketLayout` or default layout, and overrides `getBucketLayout`.

Control flow: Concrete key responses call the appropriate constructor so inherited and helper methods can route to the correct metadata tables.

State and persistence behavior: It stores only a layout value and the inherited `OMResponse`; no direct DB writes occur.

Dependencies and integration points: It is the common base for key, file, directory, ACL, multipart, purge, and delete responses.

Risks and test signals: Tests should ensure each FSO response passes or overrides the correct layout and default constructors do not accidentally route FSO operations to legacy tables.
