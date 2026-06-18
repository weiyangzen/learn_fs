# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectAclHandler.java

Purpose: `ObjectAclHandler` reserves object ACL handling for the object handler chain but currently reports it as not implemented.

Important APIs and flow: `getAction` checks for the `acl` query parameter and returns `PUT_OBJECT_ACL` only for HTTP PUT. `handlePutRequest` ignores the request if no action is selected; otherwise it throws S3 `NOT_IMPLEMENTED` for the key and updates put-object-ACL failure metrics.

State, dependencies, risks, and tests: there is no persistent state. It integrates with object operation chain action selection, query params, request method, metrics, and audit wrapper. Risks include GET object ACL falling through to another handler if not separately handled, and clients expecting ACL support receiving not implemented. Tests should verify PUT `?acl` returns not implemented, failure metrics increment, and non-ACL PUT falls through.
