# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/BucketAclHandler.java

Purpose: `BucketAclHandler` handles bucket `?acl` GET and PUT subresource requests, translating between S3 ACL XML/header grants and Ozone native ACLs.

Important APIs and flow: `shouldHandle` checks the `acl` query parameter. GET loads the bucket, verifies expected owner, converts each Ozone ACL to S3 grants, deduplicates grants across ACCESS/DEFAULT scopes, and returns `S3BucketAcl`. PUT reads grant headers or unmarshals an XML body, converts grants to bucket and volume ACL lists, resets bucket ACLs, removes old volume ACLs for affected identities, and adds new volume ACLs.

State, dependencies, risks, and tests: state is only a memoized XML unmarshaller. It integrates with Ozone volume/bucket ACL APIs, `S3Acl`, `S3BucketAcl`, metrics, and owner verification. Risks include full ACL replacement semantics, fragile comma/equal header parsing, only supported user identities, duplicated ACCESS/DEFAULT behavior, and partial failure between bucket and volume ACL updates. Tests should cover body grants, header grants, unsupported grantees, dedupe, owner condition, metrics on failure, and volume ACL synchronization.
