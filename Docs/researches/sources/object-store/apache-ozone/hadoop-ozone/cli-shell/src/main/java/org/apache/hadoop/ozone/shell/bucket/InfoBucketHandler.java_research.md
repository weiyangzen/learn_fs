## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/InfoBucketHandler.java

Purpose: bucket `info` command returning JSON bucket metadata.

Important APIs and control flow: resolves target bucket through volume/bucket lookup. If the bucket has source volume and source bucket, it wraps the object in `LinkBucket` to expose link-focused fields; otherwise it serializes the `OzoneBucket` directly. `LinkBucket` copies volume/name/source/creation/modification/owner/link fields for JSON output.

State and dependencies: read-only metadata access. Depends on `BucketHandler`, `OzoneBucket`, and JSON printing inherited from `Handler`.

Risks and test signals: wrapper field set may omit newer bucket properties for link buckets. No direct tests in this subset.
