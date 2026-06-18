## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/BucketUri.java

Purpose: picocli parameter/converter for bucket-address arguments.

Important APIs and control flow: defines positional parameter index 0 with Ozone shell URI help text and conversion through `BucketUri`. `convert` constructs an `OzoneAddress`, calls `ensureBucketAddress`, and returns the validated object.

State and dependencies: parse-time state only. Depends on `OzoneAddress` validation and shell URI documentation.

Risks and test signals: it rejects keys under buckets and missing volume/bucket names, protecting bucket handlers from accidental broader operations. No direct tests in this subset.
