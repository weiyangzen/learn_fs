<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/HddsConfServlet.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/HddsConfServlet.java

## Purpose
`HddsConfServlet` exposes running HDDS/Ozone configuration over HTTP in XML/JSON and supports tag-oriented configuration queries.

## Important APIs, Types, and Functions
It extends `HttpServlet`, owns constants `COMMAND` and static `OZONE_CONFIG`, and implements `doGet`, `getConfFromContext`, `processCommand`, `processConfigTagRequest`, `buildDescriptionMap`, `parseXmlDescriptions`, `getTextContent`, and `getOzoneConfig`.

## Control Flow
`doGet` first checks instrumentation access through `HttpServer2`, chooses response format defaulting to XML, reads `name` and `cmd`, and delegates. Without `cmd`, it writes full or named configuration as JSON or XML. With `cmd`, it handles `getOzoneTags` and `getPropertyByTag`; the latter validates `tags`, builds a description map by securely parsing configured XML resources, collects tagged properties, and writes JSON.

## State and Persistence Behavior
The servlet reads live configuration from servlet context for dump requests and uses a static `OZONE_CONFIG` for tag metadata/property lookup. It owns no persistent state; XML parsing is per request.

## Dependencies and Integration Points
It depends on servlet APIs, `OzoneConfiguration`, `HttpServer2`, `HttpServletUtils`, `JsonUtils`, Hadoop XML security utilities, DOM parsing, and configuration resource files.

## Risks and Test Signals
Risks include expensive XML parsing per tag request, static config differing from daemon live config, exposure of sensitive values if redaction is not handled by dump methods, and command validation/format errors. Tests should cover instrumentation access denial, XML/JSON output, named property lookup, invalid command/tag parameters, secure XML parsing, and tag-description enrichment.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/HddsConfServlet.java -->
