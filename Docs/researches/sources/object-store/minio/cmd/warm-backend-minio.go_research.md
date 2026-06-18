# sources/object-store/minio/cmd/warm-backend-minio.go

MinIO-specific warm-tier backend built on `warmBackendS3`. It adds optimal multipart sizing and MinIO client options such as trailing headers and disabled content SHA256.

`optimalPartSize` treats unknown size `-1` as 5 TiB, rejects objects above 5 TiB, and rounds part size up to a 128 MiB multiple under a 10,000-part limit. `PutWithMeta` uses that part size and returns the remote version ID. `newWarmBackendMinIO` validates static credentials and bucket, parses endpoint, creates a static V4 client with global remote transport, sets app info, and embeds S3 behavior for get/remove/in-use.

Risks include boundary part-size behavior, 5 TiB rejection, credential validation, and differences from generic S3 upload hashing. No direct tests in this subset cover it.
