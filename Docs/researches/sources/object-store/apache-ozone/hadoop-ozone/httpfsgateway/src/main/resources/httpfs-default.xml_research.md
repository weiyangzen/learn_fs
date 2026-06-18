# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/resources/httpfs-default.xml

## Purpose
`httpfs-default.xml` is the default HttpFS gateway configuration loaded from the classpath by `Server`. It defines HTTP binding defaults, service classes, authentication defaults, delegation token settings, filesystem access settings, and access mode.

## Important APIs, types, and functions
Key properties include `httpfs.http.port=14000`, `httpfs.http.hostname=0.0.0.0`, admin ACLs, SSL toggle, Hadoop HTTP thread/header/temp settings, `httpfs.buffer.size`, `httpfs.services`, Kerberos realm/host interpolation, Hadoop HTTP authentication settings, proxyuser examples, delegation token intervals, `httpfs.hadoop.authentication.*`, filesystem cache purge frequency/timeout, and `httpfs.access.mode`.

## Control flow
During server initialization, this file is loaded as defaults and site configuration or system properties overlay it. The `httpfs.services` list controls service startup order: instrumentation, scheduler, groups, then filesystem access.

## State and persistence behavior
The file is static configuration. It does not store runtime state but supplies defaults for in-memory server/service configuration.

## Dependencies and integration points
It references classes in this subset and Hadoop HTTP authentication keys. `FileSystemAccessService` consumes the `httpfs.hadoop.*` scoped keys after `BaseService` trims prefixes.

## Risks and edge cases
Defaults use simple authentication and local keytab/principal placeholders, so production deployments must override security settings. The access-mode description contains a `FORBIDDED` typo but behavior is implemented elsewhere. Service order matters because dependencies require instrumentation and scheduler before filesystem access.

## Test signals
`TestHttpFSMetrics` initializes `HttpFSServerWebApp`, causing this default config to load and services to start from the configured service list.
