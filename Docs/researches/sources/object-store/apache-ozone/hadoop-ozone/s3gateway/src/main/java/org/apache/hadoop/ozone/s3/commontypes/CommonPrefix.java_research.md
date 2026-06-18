# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/CommonPrefix.java

Purpose: `CommonPrefix` models a `CommonPrefixes/Prefix` entry for delimited object listing responses.

Important APIs and flow: the `Prefix` field is an `EncodingTypeObject` marshalled by `ObjectKeyNameAdapter`, allowing URL encoding when `encoding-type=url` is requested. It provides a default JAXB constructor, a convenience constructor, and accessors.

State, dependencies, risks, and tests: state is response-only. It integrates with `ListObjectResponse.addPrefix` and `BucketEndpoint` delimiter logic. Risks are incorrect URL encoding of delimiters/prefixes and null prefix handling. Tests should cover common-prefix XML with and without URL encoding.
