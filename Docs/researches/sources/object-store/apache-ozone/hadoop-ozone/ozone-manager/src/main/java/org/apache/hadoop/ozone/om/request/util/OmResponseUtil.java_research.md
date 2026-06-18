
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/OmResponseUtil.java

Purpose: Central helper for initializing successful OM response builders from requests.

Important APIs and types: Static `getOMResponseBuilder(OMRequest)` returns an `OMResponse.Builder` with request command type, `Status.OK`, trace ID, and success true.

Control flow: Single static method creates and configures the response builder.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Used broadly by OM request handlers as the common response baseline before adding operation-specific response protos or error conversion.

Risks: Assumes `request.getTraceID()` is safe for all callers; proto defaults apply when trace ID is absent. Tests should verify command type, status, success flag, and trace propagation.
