# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/KeyMetadata.java

Purpose: `KeyMetadata` is the JAXB model for one `Contents` object in a list-objects response.

Important APIs and flow: fields include URL-encodable `Key`, `Owner`, `LastModified`, `ETag`, `Size`, and `StorageClass`. `BucketEndpoint.addKey` populates it from `OzoneKey` metadata, replication config, owner, size, and modification time.

State, dependencies, risks, and tests: state is transient response data. It depends on `ObjectKeyNameAdapter`, `IsoDateAdapter`, `S3Owner`, and Ozone constants. Risks include missing/incorrect ETag quoting, null owner, incorrect storage-class mapping, and URL encoding mismatches. Tests should assert list response XML for normal keys, special characters, owners, and storage classes.
