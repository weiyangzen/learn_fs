# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/file/OMDirectoryCreateResponse.java

Purpose: `OMDirectoryCreateResponse` persists directory creation in non-FSO layouts using key-table directory marker entries.

Important APIs and types: It extends `OmKeyResponse`, stores `dirKeyInfo`, parent `OmKeyInfo` list, `Result`, `BucketLayout`, and `OmBucketInfo`, and cleans `KEY_TABLE`.

Control flow: On `Result.SUCCESS`, it writes parent directory marker keys, writes the target directory key, and updates the bucket table for namespace accounting. On `DIRECTORY_ALREADY_EXISTS`, it is an OK no-op.

State and persistence behavior: It writes key-table entries and bucket-table state, although cleanup annotation names only `KEY_TABLE`. Error/already-exists constructors avoid directory payloads.

Dependencies and integration points: It is paired with `OMDirectoryCreateRequest` and uses metadata-manager ozone dir/key naming helpers.

Risks and test signals: Tests should cover parent creation ordering, already-exists no-op, bucket namespace update, and cleanup metadata coverage.
