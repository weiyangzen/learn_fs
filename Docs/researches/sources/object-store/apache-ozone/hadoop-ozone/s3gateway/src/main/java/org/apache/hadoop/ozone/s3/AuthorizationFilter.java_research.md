# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/AuthorizationFilter.java

Purpose: `AuthorizationFilter` is the pre-matching JAX-RS request filter that parses the incoming AWS authorization material and builds the SigV4 string-to-sign before later filters mutate the request.

Important APIs and flow: the filter injects `SignatureProcessor` and request-scoped `SignatureInfo`. `filter` calls `parseSignature`, initializes `SignatureInfo`, accepts only `SignatureInfo.Version.V4`, computes the signature base through `StringToSignProducer.createSignatureBase`, and rejects missing AWS access IDs. `OS3Exception` is wrapped as a JAX-RS exception; unexpected failures become S3 internal errors.

State, dependencies, risks, and tests: state is request-scoped `SignatureInfo`; persistence is none. It integrates with signature parsers, endpoint initialization, `S3Auth`, and OM thread-local auth. Risks include unsupported SigV2/query forms being rejected here, signature canonicalization depending on unmodified request state, and generic exceptions masking malformed input as internal errors. Tests should exercise valid V4, missing access ID, unsupported version, and parser failure; endpoint integration tests indirectly require this filter to populate auth.
