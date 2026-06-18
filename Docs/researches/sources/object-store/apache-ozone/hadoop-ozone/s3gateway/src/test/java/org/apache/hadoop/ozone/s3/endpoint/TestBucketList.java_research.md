
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketList.java

Purpose: broad tests for S3 ListObjects behavior in `BucketEndpoint`.

Important APIs and control flow: helper creates stub bucket `b1` with requested keys. Tests cover root listing with delimiter, directory/prefix listing, avoiding prefix false positives, owner propagation from current UGI, empty results, prefix+delimiter common prefixes, empty-string delimiter as no delimiter, continuation-token pagination over contents and common prefixes, invalid continuation token mapping to invalid argument, `start-after`, `encoding-type=url`, unsupported encoding type, non-integer/negative/zero `max-keys`, zero max-keys in non-empty bucket, and configured `OZONE_S3G_LIST_MAX_KEYS_LIMIT` capping results.

State, dependencies, integration: mutates in-memory key maps and current login user in one owner test. Integrates endpoint query parsing, `OzoneBucketStub.listKeys`, list response DTOs, object key encoding, continuation token handling, and configuration.

Risks and test signals: changing list ordering, common-prefix accounting, continuation-token encoding, or max-key validation will break these tests. Shared UGI mutation can leak if not reset by the broader test harness. Stub shallow-list behavior is simpler than production OM but still exercises endpoint response logic.
