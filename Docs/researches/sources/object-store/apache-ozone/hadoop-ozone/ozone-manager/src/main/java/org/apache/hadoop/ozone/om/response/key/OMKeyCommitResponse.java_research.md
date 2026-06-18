# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyCommitResponse.java

Purpose: `OMKeyCommitResponse` persists committing an open key into the committed key table and handles hsync/update/delete side effects.

Important APIs and types: It stores committed `OmKeyInfo`, ozone key name, open key name, bucket info, `keyToDeleteMap`, hsync flags, optional new open-key info, and optional open key to update. It cleans open key, key, deleted, and bucket tables.

Control flow: On commit it deletes the open key unless hsync requires keeping/updating it, writes the committed key, writes any overwritten keys to deleted table, optionally updates another open key, and writes bucket used-bytes state.

State and persistence behavior: It moves data from open-key table to key table and updates deleted table for overwritten versions. Hsync can leave or update open-key state rather than deleting it.

Dependencies and integration points: It integrates key commit requests, hsync behavior, bucket quota accounting, and deleted-key cleanup.

Risks and test signals: Tests should cover normal commit, hsync commit, overwritten key deletion, open-key-to-update handling, bucket usage update, and visible `getKeysToDelete`.
