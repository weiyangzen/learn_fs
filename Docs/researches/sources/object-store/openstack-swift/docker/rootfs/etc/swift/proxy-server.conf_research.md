# sources/object-store/openstack-swift/docker/rootfs/etc/swift/proxy-server.conf

## Purpose
Docker rootfs proxy-server config exposing Swift on `0.0.0.0:8080` with debug logging and a broad middleware chain.

## Important Sections
Defaults set syslog address, `LOG_LOCAL2`, debug level, `log_name = proxy-server`, and `user = swift`. Pipeline includes catch-errors, gatekeeper, healthcheck, proxy-logging, cache, etag-quoter, listing formats, bulk, tempurl, ratelimit, s3api, tempauth, staticweb, copy, quotas, SLO/DLO, versioned writes, symlink, proxy logging, and proxy-server. Tempauth users are defined; S3API is active in the pipeline.

## Control Flow and Integration
External Docker traffic enters this proxy. Middleware performs request validation, auth, S3 compatibility, large-object/versioning/symlink handling, logging, and final proxy routing.

## State and Persistence Behavior
Proxy state is mostly externalized to backend services and memcache. Middleware creates persistent Swift metadata for versioning, large objects, quotas, tempurl behavior, symlinks, and S3-related request semantics.

## Risks and Test Signals
Tempauth users and placeholder encryption settings are not production-grade. Debug logging can expose sensitive request details if log headers are later enabled. Test signal is Docker proxy reachability, tempauth login, S3API behavior, and object/account/container operations.
