# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/ServletElementsFactory.java

Purpose: `ServletElementsFactory` centralizes construction of Jetty filter holders and mappings for `HttpServer2`.

Important APIs/types/functions: private constructor throws `UnsupportedOperationException`. `createFilterMapping(mappingName, urls)` creates a `FilterMapping`, sets path specs, dispatches to `FilterMapping.ALL`, and filter name. `createFilterHolder(filterName, classname, parameters)` creates a `FilterHolder`, sets name/class, and optional init parameters.

Control flow: `HttpServer2.addFilter()` and `addGlobalFilter()` use these helpers to install filters consistently across contexts.

State and persistence: stateless utility class.

Dependencies/integration: depends on Jetty `FilterHolder` and `FilterMapping`.

Risks: class names are strings; invalid class names fail later when Jetty initializes filters. `urls` can be null, which is used for SPNEGO in `HttpServer2` through a different path but would need Jetty-compatible handling if passed here.

Test signals: indirect coverage through `HttpServer2` filter tests and startup paths.
