# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/file/OMFileCreateResponse.java

Purpose: `OMFileCreateResponse` is the file-create response for non-FSO layouts and reuses key-create persistence.

Important APIs and types: It extends `OMKeyCreateResponse`, passes file key info, parent key infos, open key session ID, and bucket info, and cleans `KEY_TABLE` plus `OPEN_KEY_TABLE`.

Control flow: Successful construction delegates all DB batch behavior to `OMKeyCreateResponse`: parent directory markers and open key insertion. Error constructor sets the bucket layout and enforces non-OK status.

State and persistence behavior: It writes parent key markers, bucket namespace state, and an open-key table entry.

Dependencies and integration points: It bridges file request code to key response persistence for non-FSO layouts.

Risks and test signals: Tests should cover inherited open-key naming, parent directory entries, error no-op, and bucket-layout routing.
