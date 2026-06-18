
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/Application.java

Purpose: Jersey `ResourceConfig` for the S3 secret web application.

Important APIs and control flow: the constructor calls `packages("org.apache.hadoop.ozone.s3secret")`, enabling Jersey to scan the package for resources and providers, including management endpoints and request filters.

State, dependencies, integration: no mutable state after construction. Integrated from `s3g-web/WEB-INF/web.xml` through the `javax.ws.rs.Application` init-param for the `/secret/*` servlet. Depends on GlassFish Jersey.

Risks and test signals: package scanning means new providers/resources in the package are auto-registered, which is convenient but can expose annotated classes unintentionally. There is no direct unit test in the listed files; deployment descriptor correctness is the main signal.
