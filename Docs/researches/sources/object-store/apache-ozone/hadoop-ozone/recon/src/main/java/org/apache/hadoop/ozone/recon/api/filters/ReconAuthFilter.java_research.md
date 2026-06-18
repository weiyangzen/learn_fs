<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/filters/ReconAuthFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/filters/ReconAuthFilter.java

## Purpose

`ReconAuthFilter` adapts Hadoop's `ProxyUserAuthenticationFilter` for Recon HTTP authentication using Recon-specific configuration prefixes.

## Important APIs and Types

It implements `Filter`, builds auth parameters with `AuthenticationFilterInitializer.getFilterConfigMap(conf, OZONE_RECON_HTTP_AUTH_CONFIG_PREFIX)`, creates a Jetty `FilterHolder`, and initializes `ProxyUserAuthenticationFilter` with a delegated `FilterConfig`.

## Control Flow

During `init`, it builds and initializes the Hadoop auth filter. During `doFilter`, it logs the request URL at debug level and delegates all authentication behavior to `hadoopAuthFilter.doFilter`.

## State and Persistence

It stores the injected configuration and the initialized Hadoop auth filter. It persists nothing.

## Dependencies and Integration Points

It integrates with Hadoop HTTP authentication, proxy-user handling, Jetty filter metadata, servlet contexts, and Recon HTTP auth config keys.

## Risks and Edge Cases

`destroy` does not call `hadoopAuthFilter.destroy`, so delegated cleanup may be skipped. If `doFilter` is called before successful init, `hadoopAuthFilter` is null. All parameter semantics are inherited from Hadoop's auth filter.

## Test Signals

Tests should verify config-prefix extraction, init parameter forwarding, delegation to proxy-user filter, debug URL handling, and lifecycle cleanup expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/filters/ReconAuthFilter.java -->
