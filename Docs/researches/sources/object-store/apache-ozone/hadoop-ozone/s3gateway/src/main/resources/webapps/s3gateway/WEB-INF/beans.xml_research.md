
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/resources/webapps/s3gateway/WEB-INF/beans.xml

Purpose: CDI/Weld bean archive marker for the main S3 gateway web application.

Important APIs and control flow: empty beans 1.0 descriptor. It enables CDI discovery/injection in the WAR when paired with the Weld listener.

State, dependencies, integration: no state. Supports injection for Jersey resources/filters configured in the main gateway `web.xml`.

Risks and test signals: deployment depends on the servlet container honoring this legacy schema. Unit tests build endpoints manually through `EndpointBuilder`, so they do not catch CDI descriptor regressions.
