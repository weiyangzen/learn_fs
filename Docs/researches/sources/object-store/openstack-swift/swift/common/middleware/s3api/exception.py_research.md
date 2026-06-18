# sources/object-store/openstack-swift/swift/common/middleware/s3api/exception.py

Purpose: Defines internal exception types used by s3api request parsing, ACL utilities, XML helpers, and input stream validation.

Important APIs and control flow: `S3Exception` is the normal internal base for parse and ACL errors. `NotS3Request`, `ACLError`, `InvalidBucketNameParseError`, `InvalidURIParseError`, and `InvalidSubresource` carry request classification failures or diagnostics. `S3InputError` intentionally inherits `BaseException`, not `Exception`, so stream-read failures raised while downstream Swift apps consume `wsgi.input` can cut back through middleware layers to s3api and be converted to S3 responses. Subclasses represent incomplete input, size mismatch, too-small streaming chunks, malformed trailers, chunk signature mismatch, missing signing secret, SHA256 mismatch, checksum mismatch, and invalid checksum trailers; some carry expected/provided values or trailer names.

State, dependencies, and integration: These classes hold only constructor attributes. They integrate with s3request input wrappers, `S3ApiMiddleware.__call__`, and s3response error mapping.

Risks and test signals: Because `S3InputError` bypasses broad `except Exception`, callers must catch it deliberately. Tests should cover attribute preservation, BaseException behavior, middleware conversion to correct S3 errors, and that non-S3 parse exceptions do not leak raw internals.
