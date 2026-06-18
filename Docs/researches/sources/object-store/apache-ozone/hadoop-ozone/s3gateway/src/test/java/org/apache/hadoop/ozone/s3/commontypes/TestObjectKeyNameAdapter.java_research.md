
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/commontypes/TestObjectKeyNameAdapter.java

Purpose: tests `ObjectKeyNameAdapter` URL-encoding behavior for list response key/prefix names.

Important APIs and control flow: with `encodingType=url`, plain names stay readable, spaces become `+`, plus signs become `%2B`, and empty/null names return empty strings. Without encoding type, values are returned unchanged except null becomes empty.

State, dependencies, integration: no persistent state. Integrated with `ListObjectResponse` and bucket listing output when query parameter `encoding-type=url` is used.

Risks and test signals: URL encoding uses Java form-style encoding where spaces become `+`, matching the expected S3 response behavior in these tests. The tests focus on small representative strings.
