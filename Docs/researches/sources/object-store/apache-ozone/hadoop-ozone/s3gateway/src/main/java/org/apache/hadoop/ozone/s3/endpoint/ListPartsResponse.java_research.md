# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ListPartsResponse.java

Purpose: `ListPartsResponse` is the JAXB response for S3 list-parts on an active multipart upload.

Important APIs and flow: top-level fields hold bucket, key, upload ID, storage class, part marker, next part marker, max parts, truncation flag, and `Part` entries. Each part includes part number, last modified, ETag, and size. `MultipartKeyHandler` populates it from `OzoneMultipartUploadPartListParts`.

State, dependencies, risks, and tests: state is transient response data. It integrates with multipart object handlers, `IsoDateAdapter`, and Ozone part metadata. Risks include ETag fallback to part name when ETag is empty, max-parts validation occurring outside the DTO, and marker defaults. Tests should assert XML for truncated/non-truncated part lists, ETag fallback, storage class, and date formatting.
