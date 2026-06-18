# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/CompleteMultipartUploadRequestUnmarshaller.java

Purpose: this JAX-RS provider unmarshals complete-MPU XML while rejecting an empty request body early.

Important APIs and flow: it extends `MessageUnmarshaller<CompleteMultipartUploadRequest>`. `readFrom` checks `inputStream.available() == 0`, throws S3 `InvalidRequest` with "You must specify at least one part", otherwise delegates to the secure namespace-filtering unmarshaller. IO failures are wrapped as S3 invalid request errors.

State, dependencies, risks, and tests: no mutable state beyond inherited JAXB context. It integrates with Jersey body readers and object endpoint complete-MPU. Risks include `InputStream.available()` not being a reliable body-length check for all stream types and parse errors exposing parser messages. Tests should cover empty body, malformed XML, namespace/no-namespace XML, and at least-one-part validation.
