# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/PrometheusServlet.java

Purpose: `PrometheusServlet` serves Ozone/Hadoop metrics and Ratis Dropwizard metrics in Prometheus text format.

Important APIs/types/functions: `SECURITY_TOKEN` is the servlet-context attribute for optional bearer-token auth. `getPrometheusSink()` retrieves `BaseHttpServer.PROMETHEUS_SINK`. `doGet()` checks optional `Authorization: Bearer <token>`, writes sink metrics, writes a Dropwizard header, and exports `CollectorRegistry.defaultRegistry` via `TextFormat.write004()`.

Control flow: if a token is configured and the header is missing, wrong prefix, or mismatched, the servlet returns 403. Otherwise it writes Metrics2-derived sink content followed by default Prometheus registry metrics.

State and persistence: no servlet-local state. Reads sink/token from servlet context and collector registry live state.

Dependencies/integration: installed by `BaseHttpServer` at `/prom`, either as internal servlet when bearer-token auth is configured or regular servlet otherwise. Integrates with `PrometheusMetricsSink`, Prometheus Java client, and Ratis Dropwizard exporters.

Risks: bearer token comparison is direct string comparison. Tokenless secure clusters rely on the normal HTTP auth filter path. The servlet assumes a non-null sink context attribute.

Test signals: `TestPrometheusServletAuthorization` covers token acceptance/rejection behavior. Prometheus integration tests cover sink output.
