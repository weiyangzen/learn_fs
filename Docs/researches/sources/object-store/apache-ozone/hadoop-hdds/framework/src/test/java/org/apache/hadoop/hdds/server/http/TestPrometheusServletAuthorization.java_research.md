<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestPrometheusServletAuthorization.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestPrometheusServletAuthorization.java

Purpose: verifies bearer-token authorization behavior of `PrometheusServlet`.

Important APIs/types/functions: `PrometheusServlet`, `PrometheusServlet.SECURITY_TOKEN`, `BaseHttpServer.PROMETHEUS_SINK`, `PrometheusMetricsSink.writeMetrics`, servlet `init`, `doGet`, request `Authorization` header, and HTTP 403 response status.

Control flow: setup mocks servlet context/config to provide a security token and sink, then initializes the servlet. A helper invokes `doGet` with a mocked request/response and writer. The valid-token test passes `Bearer mytoken` and verifies metrics are written. Parameterized invalid headers include missing, empty, wrong scheme, wrong token, malformed spacing, and verify 403 plus no sink write.

State and persistence behavior: state is servlet instance fields initialized from mocked context attributes. No persistent state.

Dependencies and integration points: integrates servlet context initialization, HTTP authorization header parsing, and Prometheus metrics sink access control.

Risks: token comparison and header parsing are security-sensitive. Tests enforce exact bearer scheme behavior but do not cover case-insensitive schemes unless included in invalid values.

Test signals: verifies valid bearer token allows one sink write and no forbidden status; invalid headers set 403 and never call `writeMetrics`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestPrometheusServletAuthorization.java -->
