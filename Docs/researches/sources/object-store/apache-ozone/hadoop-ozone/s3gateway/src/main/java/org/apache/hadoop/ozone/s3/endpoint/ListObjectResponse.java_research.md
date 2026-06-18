# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ListObjectResponse.java

Purpose: `ListObjectResponse` is the JAXB model for `ListBucketResult`, shared by S3 list objects compatibility paths.

Important APIs and flow: fields include name, prefix, marker, max keys, key count, delimiter, encoding type, truncation flag, next continuation token, next marker, current continuation token, contents, common prefixes, and start-after. URL-sensitive fields use `ObjectKeyNameAdapter`. `BucketEndpoint` populates it while iterating Ozone keys.

State, dependencies, risks, and tests: state is response-only. It integrates with `KeyMetadata`, `CommonPrefix`, `EncodingTypeObject`, and bucket listing flow. Risks include the lowercase XML element name `continueToken`, v1/v2 compatibility fields appearing together, and key count recalculation. Tests should marshal normal, delimited, encoded, truncated, and empty listings.
