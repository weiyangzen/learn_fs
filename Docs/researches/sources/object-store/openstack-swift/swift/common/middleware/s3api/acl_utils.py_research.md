# sources/object-store/openstack-swift/swift/common/middleware/s3api/acl_utils.py

Purpose: Translates limited S3 canned or XML ACL forms into Swift container ACL headers for the non-`s3_acl` compatibility path.

Important APIs and control flow: `swift_acl_translate` maps `public-read`, `public-read-write`, `private`, `bucket-owner-full-control`, and `bucket-owner-read` to `X-Container-Read` and `X-Container-Write` values. For XML ACL input it validates `AccessControlPolicy`, inspects grants, and classifies the ACL as private, public-read, public-read-write, unsupported, or unknown. `authenticated-read` and `log-delivery-write` raise `S3NotImplemented`; unrecognized ACLs raise `ACLError`. `handle_acl_header` consumes `HTTP_X_AMZ_ACL`, clears the query string, translates the ACL, raises `InvalidArgument` on invalid canned ACLs, and injects translated Swift headers into the request.

State, dependencies, and integration: No persistent state. It depends on s3api XML helpers, XML namespace constants, and s3response exceptions. Controllers call it before Swift `POST` ACL updates.

Risks and test signals: Translation is lossy because Swift has no full per-object ACL model and public write is explicitly limited. Tests should cover XML grant combinations, unsupported grants, header deletion, query clearing, and each canned ACL mapping.
