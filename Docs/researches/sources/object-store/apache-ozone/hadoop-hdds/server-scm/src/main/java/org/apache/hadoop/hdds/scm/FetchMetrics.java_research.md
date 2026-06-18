# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/FetchMetrics.java

Purpose: JMX-to-JSON adapter that fetches platform MBean metrics and serializes them as JSON.

Important APIs and types: Public `getMetrics(String qry)`; internals use `MBeanServer`, `ObjectName`, `MBeanInfo`, `MBeanAttributeInfo`, Jackson `JsonGenerator`, `CompositeData`, and `TabularData`.

Control flow: Creates a UTF-8 JSON generator, defaults null queries to `*:*`, queries beans, writes bean metadata and readable attributes, recursively serializing arrays, numbers, booleans, composite data, tabular data, nulls, and strings.

State and persistence behavior: Holds transient MBean server and JSON factory references; persists nothing and reflects live JVM MBean state.

Dependencies and integration points: Integrates with JVM management and likely SCM/admin metrics endpoints.

Risks: Malformed queries or IO failures return null after logging. Attribute getters may throw or be expensive; failed attributes are skipped.

Test signals: Synthetic MBean tests should assert scalar, array, composite, tabular, malformed-query, and exception-skipping behavior.
