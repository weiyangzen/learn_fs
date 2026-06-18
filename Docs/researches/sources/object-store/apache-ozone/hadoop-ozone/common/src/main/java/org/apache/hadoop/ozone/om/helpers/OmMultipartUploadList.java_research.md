# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartUploadList.java

Purpose: Result container for listing in-flight multipart uploads.

Important APIs/types/functions: Builder sets uploads, next key marker, next upload ID marker, and truncation flag. Accessors expose all fields; `setUploads` can replace the upload list.

Control flow and state: Simple mutable result object. Marker defaults are empty strings.

State and persistence behavior: List response only. Upload entries are derived from multipart metadata tables.

Dependencies and integration points: Used by list multipart uploads APIs for pagination.

Risks: Upload list is not defensively copied and can be null. Mutable setter allows response mutation after construction.

Test signals: Pagination marker propagation, truncation flag, empty results, mutable list behavior, and list ordering from caller code.
