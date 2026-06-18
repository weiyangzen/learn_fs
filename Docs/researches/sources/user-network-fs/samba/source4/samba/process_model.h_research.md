<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/process_model.h -->
# sources/user-network-fs/samba/source4/samba/process_model.h

## Purpose

This header defines the process-model ABI used by Samba source4 services and loadable process-model modules.

## Important APIs, Types, and Functions

`struct model_ops` contains the model name plus callbacks for `model_init`, `accept_connection`, `new_task`, `terminate_task`, `terminate_connection`, and `set_title`. `struct process_model_critical_sizes` exposes ABI version and structure size. Public declarations include `process_model_startup()`, `register_process_model()`, `process_model_init()`, and `extern const struct model_ops single_ops`.

## Control Flow

There is no runtime flow in the header. It defines the callback contract used by `service.c`, `service_task.c`, `service_stream.c`, and the `single`, `standard`, and `prefork` implementations.

## State and Persistence Behavior

The header itself stores no state. Implementations receive opaque `process_context` values to preserve model-specific state across task, connection, and termination callbacks.

## Dependencies and Integration Points

It includes socket, service, and generated process-model prototype headers. The ABI version is used by module compatibility checks and should be bumped when callback signatures or critical semantics change.

## Risks and Edge Cases

Every model must obey ownership and event-loop expectations implied by the callback signatures. A mismatch in `process_context` type or callback lifetime can crash service code. ABI changes without `PROCESS_MODEL_VERSION` changes can break external modules.

## Test Signals

Compile coverage across all process models is the primary signal. Runtime smoke tests should start services under `single`, `standard`, and `prefork` models and exercise stream accept and task shutdown.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/process_model.h -->
