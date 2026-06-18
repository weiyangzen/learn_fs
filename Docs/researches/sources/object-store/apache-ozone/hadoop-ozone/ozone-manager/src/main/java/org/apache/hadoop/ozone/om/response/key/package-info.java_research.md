# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/package-info.java

Purpose: This package documentation marks the package as containing key response classes.

Important APIs and types: The package covers create, allocate, commit, delete, purge, rename, set-times, open-key cleanup, and shared key response bases.

Control flow: Key responses translate validated request/cache mutations into DB batch operations, with subclasses overriding status gating for partial delete/rename or special multipart-like races.

State and persistence behavior: State changes span open-key/open-file, key/file, directory, deleted, deleted-dir, bucket, snapshot info, and snapshot renamed tables depending on operation and bucket layout.

Dependencies and integration points: The package integrates request handlers, bucket layout routing, snapshot support, deletion services, hsync/open-key cleanup, and cleanup table annotations.

Risks and test signals: Tests should emphasize table-selection correctness, partial-success persistence, snapshot side effects, deleted-table key formats, and bucket quota/accounting updates.
