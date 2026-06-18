# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/HeaderPreprocessor.java

Purpose: `HeaderPreprocessor` rewrites request `Content-Type` values after signature processing so Jersey routes AWS-compatible requests to the intended resource methods.

Important APIs and flow: it records any original `Content-Type` under `X-Ozone-Original-Content-Type`. For `?delete` and requests with `uploadId`, it forces `application/xml`. For `?uploads` without `uploadId`, it uses the special `ozone/mpu` marker so multipart-upload initiation with an empty body does not get parsed as a complete-upload XML request.

State, dependencies, risks, and tests: state is only modified request headers. The filter runs after `VirtualHostStyleFilter` and after authorization so signed headers remain canonical. Risks include query-parameter precedence when both `uploads` and `uploadId` exist, and signature mismatches if the priority ordering changes. Tests should verify routing for multi-delete, complete MPU, initiate MPU, and preservation of original content type.
