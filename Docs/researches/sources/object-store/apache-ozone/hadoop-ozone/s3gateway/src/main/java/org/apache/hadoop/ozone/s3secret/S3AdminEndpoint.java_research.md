
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3AdminEndpoint.java

Purpose: JAX-RS name-binding annotation marking endpoints or methods that require S3 administrator access.

Important APIs and control flow: retained at runtime, targeted at types and methods, and annotated with `@NameBinding`. It binds matching resources to `S3SecretAdminFilter`.

State, dependencies, integration: no state. Depends on Java annotation metadata and JAX-RS `NameBinding`. Used by `S3SecretManagementEndpoint` at class level and by the provider annotation on `S3SecretAdminFilter`.

Risks and test signals: protection is opt-in; a secret endpoint not annotated with this binding would bypass the admin filter. No listed test directly exercises this annotation-filter binding.
