# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/WEB-INF/web.xml

Purpose: `web.xml` configures the Recon web application servlet container integration.

Important APIs and types: declares Servlet 3.0 web-app metadata, registers `org.apache.hadoop.ozone.recon.ReconGuiceServletContextListener`, maps `com.google.inject.servlet.GuiceFilter` to all URLs, and adds a `woff2` MIME mapping for web font delivery.

Control flow and integration: when the webapp starts, the Guice servlet context listener initializes Recon dependency injection and REST/UI bindings. All requests pass through GuiceFilter, which routes configured servlets/resources. Static assets under the Recon webapp rely on MIME mappings for correct browser behavior.

State and persistence: no application state in this file. It influences runtime startup and request routing.

Dependencies: Java Servlet API and Guice Servlet.

Risks and test signals: startup tests should verify listener initialization, Guice filter mapping, and static asset MIME delivery. A broken listener class or filter mapping can prevent the REST API and UI from serving.
