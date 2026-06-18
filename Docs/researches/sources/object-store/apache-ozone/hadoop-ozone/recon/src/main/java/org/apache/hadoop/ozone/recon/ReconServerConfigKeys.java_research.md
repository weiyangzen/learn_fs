# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconServerConfigKeys.java

## Purpose
`ReconServerConfigKeys` defines Recon-specific configuration keys and defaults for HTTP service, DB paths, OM/SCM sync, task execution, metrics collection, container reconciliation, and exports.

## Important APIs, Types, And Functions
The class is a public unstable constants holder. Key groups include HTTP/SPNEGO settings, Recon DB and snapshot directories, OM snapshot intervals and timeouts, task thread/buffer counts, SCM sync intervals, DataNode metrics collection settings, container ID/deleted-container batch sizes, unhealthy-container fetch size, and export queue/download/directory settings.

## Control Flow
There is no executable flow. Runtime code reads these constants through `OzoneConfiguration`, `ReconHttpServer`, `ReconControllerModule`, task controllers, metrics services, SCM sync code, and export managers.

## State And Persistence
No mutable state exists. The constants define persistence locations and operational defaults used elsewhere.

## Dependencies And Integration Points
It is referenced by server startup, HTTP server, SQL config URL resolution, OM/SCM providers, `DataNodeMetricsService`, and container export/listing paths.

## Risks
Changing defaults can have large operational impact on memory, SCM lock pressure, network payloads, task concurrency, and export storage. Deprecated legacy keys still exist for compatibility in nearby configuration providers.

## Test Signals
Tests should verify defaults are consumed correctly, deprecated aliases map correctly, batch caps in consuming code honor comments, and exported config docs include these annotated keys where appropriate.
