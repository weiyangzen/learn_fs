# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/AbstractS3MultipartAbortResponse.java

Purpose: `AbstractS3MultipartAbortResponse` centralizes abort persistence for multipart uploads, moving uploaded parts to the deleted table and removing MPU bookkeeping.

Important APIs and types: It extends `OmKeyResponse`, uses `OmMultipartAbortInfo`, `OmMultipartKeyInfo`, `PartKeyInfo`, `OmKeyInfo`, `RepeatedOmKeyInfo`, `OmUtils.prepareKeyForDelete`, and bucket layout-specific open-key tables.

Control flow: For each abort info, it deletes the multipart open key, deletes the multipart info row, iterates part key infos, converts each part to `OmKeyInfo`, wraps it for deletion, writes deleted-table entries, and finally updates bucket used bytes. A convenience overload builds a singleton `OmMultipartAbortInfo`.

State and persistence behavior: It mutates open-key/open-file table, multipart info table, deleted table, and bucket table in one batch.

Dependencies and integration points: It is reused by single abort and expired MPU cleanup responses across default and FSO layouts.

Risks and test signals: Tests should cover multiple parts, empty part maps, bucket layout routing, deleted-table key naming using multipart key/upload ID, and bucket quota update.
