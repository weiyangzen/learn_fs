# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/bucket.py

Purpose: Implements S3 bucket metadata, create, delete, and object-listing APIs on top of Swift containers.

Important APIs and control flow: `HEAD` returns Swift container headers as S3 OK. `_parse_request_options` validates `encoding-type`, handles v1 listings, v2 listings, and object-version listings, and translates S3 markers into Swift query params. Listing builders create `ListBucketResult` or `ListVersionsResult`, including pagination markers, owner data, common prefixes, delete markers, S3 timestamps, quoted ETags, SLO-derived ETags, and storage class. `GET` requests JSON listings from Swift with `limit=max_keys+1`, detects truncation, and serializes XML. `PUT` validates optional `CreateBucketConfiguration` against configured location, then creates the Swift container and normalizes status/location. `DELETE` optionally deletes the multipart segments container before deleting the main bucket. `_delete_segments_bucket` refuses non-empty/versioned buckets and deletes segment objects iteratively.

State, dependencies, and integration: Persistent state is Swift containers, segment containers, object versioning sysmeta, and storage policy info. It depends on XML validation, Swift listing JSON, S3 timestamps, and multipart suffix conventions.

Risks and test signals: Segment cleanup has race warnings around concurrent complete uploads. Tests should cover v1/v2/version listing pagination, encoding URL behavior, invalid version markers, SLO ETag handling, bucket location mismatch, non-empty/versioned delete failures, segment deletion errors, and malformed Swift listing responses.
