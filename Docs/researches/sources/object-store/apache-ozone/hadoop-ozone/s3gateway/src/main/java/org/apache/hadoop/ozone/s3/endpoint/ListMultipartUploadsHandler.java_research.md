# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ListMultipartUploadsHandler.java

Purpose: `ListMultipartUploadsHandler` handles bucket `?uploads` requests that list in-progress multipart uploads.

Important APIs and flow: it claims requests with the `uploads` query parameter, sets `LIST_MULTIPART_UPLOAD`, reads key marker, upload ID marker, prefix, and max uploads, caps max uploads at 1000, rejects values less than one, verifies bucket owner, calls `OzoneBucket.listMultipartUploads`, and maps Ozone upload entries into `ListMultipartUploadsResult.Upload` with storage class.

State, dependencies, risks, and tests: no persistent state exists. It integrates with Ozone multipart listing, bucket handler chain, metrics, owner verification, and response DTOs. Risks include not supporting delimiter semantics here, max-upload parsing/capping behavior, and exception mapping through outer endpoint code. Tests should cover markers, prefix, max upload validation/capping, owner mismatch, truncation markers, and storage-class mapping.
