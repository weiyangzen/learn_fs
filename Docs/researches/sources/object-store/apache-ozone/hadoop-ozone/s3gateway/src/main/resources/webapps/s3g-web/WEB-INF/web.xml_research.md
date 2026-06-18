
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/resources/webapps/s3g-web/WEB-INF/web.xml

Purpose: deployment descriptor for the S3 secret web application.

Important APIs and control flow: declares Jersey `ServletContainer` named `secret`, configured with `org.apache.hadoop.ozone.s3secret.Application`, loaded on startup, and mapped to `/secret/*`. Registers Weld servlet listener for CDI.

State, dependencies, integration: no application state. Integrates servlet container, Jersey application scanning, and CDI injection for the `org.apache.hadoop.ozone.s3secret` package.

Risks and test signals: any mismatch in application class name or servlet mapping would make secret endpoints unavailable. The descriptor exposes only `/secret/*`, relying on filters and config for security. No direct web-container test is present in this subset.
