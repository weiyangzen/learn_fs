## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/GetAclBucketHandler.java

Purpose: bucket-specific `getacl` command with optional link-source ACL resolution.

Important APIs and control flow: mixes in `BucketUri`, adds `--source` to fetch source bucket ACLs for link buckets, and otherwise delegates to `GetAclHandler`. `getSourceObj` recursively follows link buckets by reading bucket metadata and rebuilding `OzoneObj` for the source until a non-link bucket is reached.

State and dependencies: read-only ACL and bucket metadata access. Depends on `GetAclHandler`, `BucketUri`, `OzoneObjInfo`, and Ozone client bucket link fields.

Risks and test signals: recursive link resolution lacks explicit cycle detection; server-side link constraints likely prevent cycles, but this handler assumes that. No direct tests in this subset.
