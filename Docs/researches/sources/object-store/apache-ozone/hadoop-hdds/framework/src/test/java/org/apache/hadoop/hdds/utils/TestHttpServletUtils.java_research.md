<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestHttpServletUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestHttpServletUtils.java

Purpose: tests servlet response-format negotiation and error-response rendering in `HttpServletUtils`.

Important APIs/types/functions: `HttpServletUtils.getResponseFormat`, `writeErrorResponse`, `HttpHeaders.ACCEPT`, servlet request/response mocks, `PrintWriter`, and response formats JSON/XML.

Control flow: parameterized cases stub the Accept header and assert selected response format. Separate tests mock response writers, call error writer for JSON and XML, and compare exact serialized error bodies.

State and persistence behavior: uses in-memory `StringWriter` output and mocked servlet objects. No durable state.

Dependencies and integration points: integrates servlet HTTP content negotiation with Ozone utility error serialization.

Risks: exact XML/JSON strings can be brittle if serializer formatting changes, but they pin the public error body contract. Accept-header parsing may need more cases for quality values or multiple content types.

Test signals: asserts format selection for provided Accept values and exact JSON/XML error output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestHttpServletUtils.java -->
