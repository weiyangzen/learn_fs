
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/resources/META-INF/beans.xml

Purpose: CDI/Weld bean archive marker for the module-level resources.

Important APIs and control flow: empty `<beans>` document using Java EE beans 1.0 schema. Its presence enables CDI scanning/injection for application classes packaged with this resource.

State, dependencies, integration: no mutable state. Works with Weld listener declared in web descriptors and `@Inject` fields/constructors in S3 gateway resources and filters.

Risks and test signals: empty descriptor relies on container defaults. If omitted or schema handling changes, injection of `OzoneConfiguration` and other beans may fail. No direct listed test exercises deployment-time CDI boot.
