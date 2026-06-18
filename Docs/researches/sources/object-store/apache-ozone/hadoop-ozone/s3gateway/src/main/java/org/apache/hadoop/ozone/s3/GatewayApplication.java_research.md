# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/GatewayApplication.java

Purpose: `GatewayApplication` is the Jersey `ResourceConfig` that exposes the S3 Gateway REST resources and filters.

Important APIs and flow: the constructor calls `packages("org.apache.hadoop.ozone.s3")`, causing Jersey to scan endpoint resources, filters, exception mappers, producers, and providers under the S3 package tree.

State, dependencies, risks, and tests: the class has no mutable state or persistence. It depends on Jersey server package scanning and module classpath completeness. Risks are package scanning being too broad or missing resources moved outside the package. Test signal is application startup and endpoint discovery in Jersey/container tests.
