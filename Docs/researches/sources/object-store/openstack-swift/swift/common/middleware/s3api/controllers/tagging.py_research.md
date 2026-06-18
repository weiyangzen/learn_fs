# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/tagging.py

Purpose: Provides minimal tagging subresource compatibility.

Important APIs and control flow: `TaggingController.GET` returns an empty `Tagging` XML document containing an empty `TagSet` for either bucket or object tagging requests. `PUT` and `DELETE` both raise `S3NotImplemented`.

State, dependencies, and integration: No tag state is stored or read. It depends only on controller base classes, XML helpers, and s3response exceptions. Access control and resource routing are handled outside this file by s3request and ACL handlers.

Risks and test signals: Returning empty tags for GET while rejecting writes may be acceptable for clients that probe tags but can surprise clients expecting persisted tag state. Tests should cover GET XML for bucket and object forms, content type behavior, PUT/DELETE 501 responses, and access-control prechecks.
