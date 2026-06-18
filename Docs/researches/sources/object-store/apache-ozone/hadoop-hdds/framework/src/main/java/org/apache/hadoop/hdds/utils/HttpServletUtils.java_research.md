# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/HttpServletUtils.java

## Purpose
`HttpServletUtils` provides shared servlet response helpers for Ozone HTTP endpoints. It chooses JSON/XML response formats from the `Accept` header, writes formatted error bodies, writes generic formatted content through a checked callback, and exposes a small `ResponseFormat` enum.

## Important APIs and Types
`getResponseFormat(HttpServletRequest)` returns `JSON`, `XML`, or `UNSPECIFIED`. `writeErrorResponse` sets status and emits either a JSON `{"error": ...}` object or secure XML `<error>` document. `writeResponse` sets content type and invokes a `CheckedConsumer<Writer>`, rethrowing caller-declared exception types. `ResponseFormat.getContentType` maps JSON/XML to UTF-8 media types.

## Control Flow and State
The class is stateless except for a memoized secure `DocumentBuilderFactory` supplier. XML error creation builds a DOM document and transforms it with Hadoop secure XML utilities. Format detection treats any accept header containing `json` as JSON and otherwise defaults to XML for compatibility.

## Persistence, Dependencies, and Integration
There is no persistence. Dependencies include servlet APIs, JAX-RS media/header constants, Ozone `JsonUtils`, Hadoop `XMLUtils`, and Ratis memoized checked suppliers. This class is intended for web UI and REST-like endpoint handlers that need consistent response formatting.

## Risks and Test Signals
`UNSPECIFIED` has no content type and is not supported by `writeErrorResponse`, so callers must normalize or handle unspecified formats before writing errors. Accept-header parsing is substring-based rather than full content negotiation. Tests should cover null/mixed accept headers, secure XML escaping, callback exception propagation, content types, and unsupported format behavior.
