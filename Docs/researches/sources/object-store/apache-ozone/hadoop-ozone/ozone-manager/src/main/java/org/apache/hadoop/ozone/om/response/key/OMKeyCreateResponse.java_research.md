# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyCreateResponse.java

Purpose: `OMKeyCreateResponse` persists open-key creation for default-layout key creates and parent directory marker creation.

Important APIs and types: It extends `OmKeyResponse`, stores `OmKeyInfo`, open key session ID, parent key infos, and bucket info, and cleans open-key, key, and bucket tables.

Control flow: `addToDBBatch` writes each parent directory marker into the key table, updates bucket namespace state when parents were created, derives the open key with session ID, and writes the open-key table entry.

State and persistence behavior: It stages in-progress key state in open-key table, not committed key table. Parent directory markers and bucket quota state may also be persisted.

Dependencies and integration points: It supports key/file create request flows and later commit/abort operations.

Risks and test signals: Tests should cover parent marker creation, no-parent fast path, open-key naming, bucket update, and failure response no-op.
