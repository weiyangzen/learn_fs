# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/CompleteMultipartUploadResponse.java

Purpose: `CompleteMultipartUploadResponse` is the JAXB XML result model for a successful complete-MPU request.

Important APIs and flow: fields are `Location`, `Bucket`, `Key`, and `ETag` under `CompleteMultipartUploadResult`. Object endpoint code populates these after Ozone completes multipart assembly.

State, dependencies, risks, and tests: state is transient response data. It integrates with JAXB and Ozone MPU completion metadata. Risks are incorrect ETag quoting/location format and null fields for edge cases. Tests should assert XML shape and ETag/location content after complete MPU.
