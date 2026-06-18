# sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/pom.xml

Purpose: Maven module descriptor for `ozone-s3-secret-store`, packaged as a jar under the Apache Ozone parent at version `2.3.0-SNAPSHOT`.

Important APIs and control flow: Declares module identity, UTF-8 encoding, source download property, and dependencies needed to implement remote S3 secret storage: BetterCloud Vault Java driver, Jakarta annotations, Hadoop common, Ozone common, Ozone manager, and SLF4J API. The compiler plugin disables annotation processing with `<proc>none</proc>`.

State and persistence behavior: No runtime state. Build metadata controls classpath and artifact packaging for the Vault-backed S3 secret-store provider.

Dependencies and integration points: This module depends on Ozone OM interfaces (`S3SecretStore`, `S3SecretStoreProvider`, helper value types) and the Vault driver. It integrates into the larger Ozone build through the parent POM.

Risks and test signals: Build risk centers on Vault driver API compatibility and disabled annotation processing. The POM contains no tests or plugin executions beyond compilation configuration.
