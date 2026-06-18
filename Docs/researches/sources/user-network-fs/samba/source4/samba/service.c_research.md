<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service.c -->
# sources/user-network-fs/samba/source4/samba/service.c

## Purpose

`service.c` manages registration and startup of named Samba source4 server services.

## Important APIs, Types, and Functions

The private linked list `registered_servers` stores service names and copied `service_details`. `register_server_service()` adds entries. `server_service_startup()` selects a process model and starts all configured service names. `server_service_init()` maps a configured name to the registered service and invokes `task_server_startup()`. `samba_service_init()` loads static and shared service modules.

## Control Flow

`server.c` calls `samba_service_init()` during startup. Later it calls `server_service_startup()` with `server services` from loadparm and a parent-control fd. Each configured service name is looked up case-insensitively, and task startup is delegated to the selected process model.

## State and Persistence Behavior

Service registration is process-global memory. `service_details` is copied during registration, so callers do not need to preserve the original structure. No disk state is written.

## Dependencies and Integration Points

The file integrates Samba module loading, process models, and task service startup. Static modules come from `STATIC_service_MODULES`.

## Risks and Edge Cases

An unknown service name returns `NT_STATUS_INVALID_SYSTEM_SERVICE` and aborts service startup. Registration does not reject duplicate service names, so the first matching entry wins. The copied `service_details` may contain function pointers that must remain valid for the process lifetime.

## Test Signals

Tests should register fake services, verify configured startup order, unknown-service failure, static/shared service module loading, and process-model startup failure propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/service.c -->
