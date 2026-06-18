# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/OMKeyDeleteResponse.java

Purpose: `OMKeyDeleteResponse` persists deleting one committed key in default layouts and records non-empty key data for asynchronous block deletion.

Important APIs and types: It extends `AbstractOMKeyDeleteResponse`, stores `OmKeyInfo`, bucket info, and optional deleted open-key info for hsync cleanup metadata.

Control flow: It derives the committed key name, calls `addDeletionToBatch` on the key table, writes updated bucket state, and, when an hsync open key exists, writes its metadata back to the open-key table for cleanup service processing.

State and persistence behavior: It deletes from key table, writes deleted table for non-empty keys, updates bucket table, and may update open-key table.

Dependencies and integration points: It integrates key delete requests, hsync cleanup, bucket quota accounting, and key deletion service.

Risks and test signals: Tests should cover empty and non-empty key deletion, deleted-table key format, hsync metadata path, bucket update, and failed response no-op.
