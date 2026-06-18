# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/versioning.py

Purpose: Implements S3 bucket versioning subresource behavior using Swift object-versioning support.

Important APIs and control flow: `VersioningController.GET` is bucket-scoped, reads container sysmeta through `req.get_container_info`, and returns `VersioningConfiguration` with `Status` set to `Enabled` or `Suspended` when `versions-enabled` sysmeta exists. `PUT` requires Swift's `object_versioning` feature in the Swift info registry, parses and validates `VersioningConfiguration` XML with a bounded body size, accepts only `Enabled` or `Suspended`, sets `X-Versions-Enabled` to a lowercase boolean, POSTs the container, and returns OK.

State, dependencies, and integration: Persistent state is container sysmeta managed by Swift's object versioning middleware. It depends on `/info` feature registration, XML schema validation, and the bucket operation decorator.

Risks and test signals: Versioning availability and status mapping must align with the versioned-writes middleware. Tests should cover unavailable feature 501, malformed or missing XML, invalid statuses, sysmeta true/false GET mapping, POST header value, and object-key coercion to bucket requests.
