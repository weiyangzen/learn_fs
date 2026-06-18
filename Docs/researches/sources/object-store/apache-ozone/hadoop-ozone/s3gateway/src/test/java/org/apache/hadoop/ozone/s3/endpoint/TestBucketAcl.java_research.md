
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketAcl.java

Purpose: tests bucket ACL GET and PUT behavior through `BucketEndpoint`.

Important APIs and control flow: setup creates an S3 bucket, mocked servlet/header state, and endpoint with `?acl`. Tests cover reading ACLs, setting grant headers for READ/WRITE/READ_ACP/WRITE_ACP/FULL_CONTROL, multiple grants, replacing old ACLs, body XML parsing for user grants, rejecting group grants, bucket-not-found mapping, invalid XML wrapping as invalid request, invalid/whitespace grant headers as invalid argument, empty grant header as no-op success, and header precedence over XML body when both are present.

State, dependencies, integration: mutates in-memory bucket/volume ACL lists in stubs. Reads XML resources from test classpath. Integrates `BucketEndpoint`, `BucketAclHandler`/ACL conversion classes, JAX-RS responses, and `OzoneAcl`.

Risks and test signals: assertions around volume ACLs in `testPutClearOldAcls` show nuanced mapping from S3 grants to Ozone ACLs and may be easy to regress. Header-over-body precedence is explicitly protected. Tests use mocked `parameterMap`, while the built endpoint also has query-params-for-test set, so there are two query mechanisms in play.
