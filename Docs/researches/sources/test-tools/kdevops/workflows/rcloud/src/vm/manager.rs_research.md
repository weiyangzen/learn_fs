<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/vm/manager.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/vm/manager.rs

## Purpose
`VmManager` is the core rcloud lifecycle implementation. It connects HTTP requests to libvirt domains, qcow2 disks, guest customization, XML generation, and image discovery.

## Important Types and Functions
`VmSpec` describes create inputs: name, vcpus, memory, base image, root disk size, optional SSH user, and optional public key content. `VmManager::new(config)` stores `AppConfig`. `connect()` opens libvirt. Lifecycle methods are `create_vm`, `list_vms`, `get_vm`, `start_vm`, `stop_vm`, and `destroy_vm`. Supporting methods include `customize_vm_disk`, `get_vm_info_from_domain`, `get_domain_ip_address`, `parse_domifaddr_output`, and `list_base_images`. `VmInfo` is the internal response shape.

## Control Flow
`create_vm` generates a UUID, validates base image existence, computes disk paths, creates a COW disk, customizes it with `virt-customize` if SSH data is available, infers UEFI needs from the image name, generates simple libvirt XML, defines the domain, starts it, and returns the libvirt UUID. It cleans up disks, directories, and domains on customization, define, or start failures. Other lifecycle methods look up domains by UUID or name and call libvirt operations.

## State, Persistence, and Dependencies
VM state is persisted in libvirt domain definitions, running QEMU instances, NVRAM for UEFI guests, and qcow2 disk files under the storage pool. The manager depends on libvirt Rust bindings, `qemu-img`, `virt-customize`, `sudo virsh domifaddr`, filesystem paths, UUID generation, and XML generation.

## Risks and Test Signals
Blocking process and libvirt calls run synchronously under async HTTP handlers. User-controlled names and SSH usernames are interpolated into filesystem paths and shell commands passed to `virt-customize --run-command`, so validation is important. IP lookup requires sudo virsh permissions and guest/network support. `domain.shutdown()` is graceful and may not stop immediately. Strong tests need isolated path helper tests, XML tests, mocked command execution, and real integration tests behind a libvirt-capable environment.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/vm/manager.rs -->
