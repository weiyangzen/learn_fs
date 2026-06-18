# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/CompleteMultipartUploadRequest.java

Purpose: `CompleteMultipartUploadRequest` is the JAXB request model for S3 Complete Multipart Upload XML.

Important APIs and flow: the root element is `CompleteMultipartUpload` in the S3 namespace. It contains a list of `Part` elements, each with `PartNumber` and `ETag`. The object endpoint consumes this model after XML unmarshalling to complete an MPU in Ozone.

State, dependencies, risks, and tests: state is request body data only. It integrates with `CompleteMultipartUploadRequestUnmarshaller` and object MPU completion. Risks include accepting unordered, duplicate, missing, or empty part lists unless later validation catches them. Tests should unmarshal namespace and non-namespace XML and validate downstream error handling for bad parts.
