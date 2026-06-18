# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartCommitUploadPartInfo.java

Purpose: Response DTO for committing one multipart upload part.

Important APIs/types/functions: Constructor sets part name and ETag; getters expose both.

Control flow and state: Immutable after construction.

State and persistence behavior: Response only. The actual part metadata is persisted through multipart key/part tables.

Dependencies and integration points: Returned by commit-multipart-part request handling and used by S3 MPU APIs.

Risks: No validation of part name or ETag.

Test signals: Commit-part response tests should verify ETag and part name propagation, including overwrite/recommit cases.
