# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/ObjectKeyNameAdapter.java

Purpose: `ObjectKeyNameAdapter` marshals `EncodingTypeObject` values into S3-compliant object key text for XML responses.

Important APIs and flow: `marshal` checks whether encoding type is `"url"`. If so, it calls `S3Utils.urlEncode` and then restores encoded slash `%2F` to `/`, matching S3 list response conventions. Without URL encoding, it returns the raw name. `unmarshal` is unsupported.

State, dependencies, risks, and tests: no mutable state exists. It integrates with `CommonPrefix`, `KeyMetadata`, and list response prefix/delimiter fields. Risks include unsupported unmarshal reuse, special-character encoding differences, and preserving `/` when callers expected full percent encoding. Tests should cover spaces, unicode/control-safe characters, slashes, and non-url encoding.
