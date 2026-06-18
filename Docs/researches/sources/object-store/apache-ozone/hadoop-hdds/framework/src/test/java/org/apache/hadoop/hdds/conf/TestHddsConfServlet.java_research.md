# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/conf/TestHddsConfServlet.java

## Purpose

This JUnit class verifies `HddsConfServlet` and shared servlet response helpers for configuration dump, single-property lookup, tag discovery, tag-based lookup, JSON serialization, XML serialization, and error handling.

## Important APIs, Types, And Functions

Important helpers are `getResultWithCmd()`, `verifyGetProperty()`, `getTestConf()`, and `getPropertiesConf()`. The nested `OzoneTestConfig` class supplies annotated config metadata through `@ConfigGroup` and `@Config`. The tests exercise `HddsConfServlet.doGet`, `HttpServletUtils.writeResponse`, `OzoneConfiguration.dumpConfiguration`, `OzoneConfiguration.TAGS`, `OzoneConfiguration.getObject`, and `OzoneConfiguration.writeXml`.

## Control Flow

Each servlet test constructs an `OzoneConfiguration`, mocks `ServletConfig`, `ServletContext`, request, and response, injects the configuration through `HttpServer2.CONF_CONTEXT_ATTRIBUTE`, invokes `doGet`, and inspects the captured writer output. Property lookup iterates across XML and JSON accept headers and across found, missing, empty, and null names. Command tests dispatch through `cmd=getOzoneTags`, `cmd=getPropertyByTag`, and an illegal command.

## State And Persistence

State is in-memory only: static test maps, mock request parameters, a per-test `OzoneConfiguration`, and `StringWriter` output. The nested annotated config object is registered into the configuration metadata cache by `conf.getObject(OzoneTestConfig.class)`.

## Dependencies And Integration Points

The tests integrate servlet APIs, Mockito, AssertJ, Jackson JSON parsing, secure XML parsing via `XMLUtils`, and HDDS HTTP response utilities. They protect the UI endpoint consumed by `ozone.js`.

## Risks

The test compares exact XML for invalid commands, so harmless formatter changes can break it. `TEST_FORMATS.get(null)` intentionally produces a null accept header in command tests; servlet default-format behavior must remain stable. The tests do not parse the full XML/JSON single-property responses structurally.

## Test Signals

Signals include 404 status for missing properties, inclusion/exclusion of config keys in responses, presence of programmatic resource metadata in JSON, valid XML parse with expected value, tag JSON equality, and illegal-command XML error output.
