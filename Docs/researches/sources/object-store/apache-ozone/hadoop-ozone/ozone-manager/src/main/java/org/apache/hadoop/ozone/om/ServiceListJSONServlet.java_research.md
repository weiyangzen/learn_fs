# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ServiceListJSONServlet.java

Purpose: `ServiceListJSONServlet` exposes OM's service list as pretty-printed JSON over the OM HTTP server, typically under `/serviceList`.

Important APIs and types: It extends `HttpServlet`, reads the `OzoneManager` from `OzoneConsts.OM_CONTEXT_ATTRIBUTE` in `init`, and implements `doGet`. It uses Jackson `ObjectMapper` with `SerializationFeature.INDENT_OUTPUT`.

Control flow: `doGet` sets the JSON content type, obtains the response writer, serializes `om.getServiceList()`, writes it, and closes the writer in a finally block. IO exceptions are logged and mapped to HTTP 500.

State and persistence behavior: The servlet keeps a transient reference to `OzoneManager` and persists nothing. Response content reflects live OM service metadata.

Dependencies and integration points: It integrates with OM's embedded HTTP server and the service discovery data used by clients and diagnostics.

Risks and test signals: Null OM context would cause failures on request. Closing the writer is acceptable but makes further servlet filters unable to append. Tests should cover JSON content type, successful serialization, missing/failed OM service list handling, and HTTP 500 on writer or serialization errors.
