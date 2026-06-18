# sources/distributed-fs/tahoe-lafs/src/allmydata/web/storage_plugins.py

## Purpose
Provides a parent Twisted resource for web resources contributed by enabled storage client plugins. It dispatches child path segments to plugin-provided resources by name.

## Important APIs, Types, And Functions
`StoragePlugins` is the only class. It stores the Tahoe client and implements `getChild(segment, request)`, using `client.get_client_storage_plugin_web_resources()` to retrieve a mapping from plugin names to `IResource` objects.

## Control Flow
On child traversal, the segment is decoded as UTF-8 and used as a key into the plugin resource mapping. If found, the resource is cached with `putChild(segment, result)` and returned. If not found, `NoResource()` is returned.

## State And Persistence
The resource holds only the client reference and Twisted child-resource cache entries created by `putChild`. It does not persist plugin state or modify plugin configuration.

## Dependencies And Integration Points
It depends on Twisted `Resource`/`NoResource` and the client method `get_client_storage_plugin_web_resources`. It is a narrow extension point for Tahoe storage plugins that expose web UI/API resources.

## Risks And Test Signals
Risks include UTF-8 decode failures for arbitrary path bytes, stale cached child resources if the plugin resource mapping changes after first access, and name collisions between plugins. Tests should cover known plugin child lookup, unknown child lookup, non-ASCII plugin names if supported, and whether dynamic plugin enable/disable behavior is expected to reflect after caching.
