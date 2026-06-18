<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/process_model.c -->
# sources/user-network-fs/samba/source4/samba/process_model.c

## Purpose

`process_model.c` manages registration and lookup of Samba source4 process models. Process models decide how server services create tasks, accept stream connections, terminate work, and set process titles.

## Important APIs, Types, and Functions

The private `struct process_model` stores a `const struct model_ops *` plus an `initialised` flag. `register_process_model()` appends a model after duplicate-name checks. `process_model_startup()` locates a model by name, runs its `model_init()` once, and returns its ops. `process_model_init()` loads static and shared modules in the `process_model` class. `process_model_version()` returns `PROCESS_MODEL_VERSION` and `sizeof(struct model_ops)` for module ABI checks.

## Control Flow

`server.c` calls `process_model_init()` during daemon startup, which runs static and shared process-model init functions. Later, `server_service_startup()` calls `process_model_startup(model)`. The selected model's ops are passed into task and stream service startup.

## State and Persistence Behavior

The registered model table is process-global talloc memory. Each model is initialized at most once per process. No persistent disk state is written.

## Dependencies and Integration Points

It depends on `samba/process_model.h`, loadparm context, and Samba module-loading helpers. Static modules come from build-generated `STATIC_process_model_MODULES`.

## Risks and Edge Cases

Unknown model names call `exit(-1)`, so configuration mistakes abort startup. The registry is global and not synchronized; initialization is expected during single-threaded startup. Duplicate registration returns `NT_STATUS_OBJECT_NAME_COLLISION`.

## Test Signals

Tests should verify all built-in models register, duplicate registration fails, shared modules load, unknown model startup exits or is caught by integration tests, and selected `model_init()` is called only once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/process_model.c -->
