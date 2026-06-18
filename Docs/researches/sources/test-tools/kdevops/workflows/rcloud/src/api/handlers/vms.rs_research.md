<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/vms.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/vms.rs

## Purpose
This module implements VM lifecycle REST handlers for create, list, get, start, stop, and destroy operations. It is the HTTP bridge between API models and `VmManager`.

## Important APIs and Functions
`create_vm(config, req)` maps `CreateVmRequest` into `VmSpec` and returns `CreateVmResponse`. `list_vms(config)` maps `VmInfo` values into `VmResponse` objects inside `ListVmsResponse`. `get_vm(config, vm_id)`, `start_vm`, `stop_vm`, and `destroy_vm` delegate by id or name through `VmManager` and return JSON status or errors.

## Control Flow
Every handler constructs a new `VmManager` from a cloned `AppConfig`. Operations are synchronous inside async handlers. Success paths return 201 for create and 200 for the other operations. `get_vm` converts manager errors to 404; other lifecycle errors become 500.

## State, Persistence, and Dependencies
State changes are delegated to libvirt and disk operations in `VmManager`. The handlers themselves only transform request and response shapes. Dependencies include Actix Web extractors, API model structs, `AppConfig`, `VmManager`, `VmSpec`, tracing, and `serde_json` for error/status objects.

## Risks and Test Signals
There is no input validation for VM name, CPU count, memory, disk size, base image name, SSH username, or SSH key content before reaching the manager. Blocking libvirt and process work in async handlers can occupy Actix workers. Error mapping is coarse and may expose internal messages. Tests should cover serialization, validation failures, not-found behavior, and manager integration with mocked or isolated libvirt.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/vms.rs -->
