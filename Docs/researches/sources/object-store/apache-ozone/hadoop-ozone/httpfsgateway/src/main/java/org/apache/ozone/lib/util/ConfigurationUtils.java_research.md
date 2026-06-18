# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/util/ConfigurationUtils.java

## Purpose
`ConfigurationUtils` wraps common Hadoop `Configuration` copy, default injection, resolution, and XML loading operations used by the server framework.

## Important APIs, types, and functions
`copy(source, target)` overwrites target entries with all source entries. `injectDefaults(source, target)` sets only missing target keys. `resolve(conf)` creates a new configuration with values resolved through `conf.get(key)`. `load(conf, inputStream)` delegates to `Configuration#addResource`.

## Control flow
All methods validate required arguments. Iteration uses Hadoop `Configuration`'s entry iterator.

## State and persistence behavior
No static state exists. Methods mutate provided target configurations and read input streams via Hadoop configuration parsing.

## Dependencies and integration points
`Server` uses this class for default/site config merging. `BaseService` uses `resolve` before trimming service prefixes. `GroupsService` and `FileSystemAccessService` use it to copy scoped config.

## Risks and edge cases
`copy` and `injectDefaults` iterate effective configuration entries, which may include defaults depending on the source. `resolve` materializes substituted values, which is useful for services but can obscure original variable references.

## Test signals
Service boot and configuration-based behavior provide indirect coverage.
