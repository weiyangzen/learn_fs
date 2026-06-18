<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/vm/xml.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/vm/xml.rs

## Purpose
This module renders libvirt domain XML for rcloud VMs. It supports both a Tera-template path and a currently used simple string generator.

## Important Types and Functions
`VmXmlContext` holds fields expected by guestfs/kdevops XML templates, including hostname, memory, vcpu count, storage paths, network device, QEMU binary path, UEFI flag, host passthrough, and GDB toggle. `VmXmlContext::new` builds default context values. `render_vm_xml(template_path, context)` loads a template, registers it with Tera, inserts all context fields, and renders XML. `generate_simple_vm_xml` directly formats a libvirt `<domain type='kvm'>` using q35 machine, qcow2 virtio disk, network interface, serial console, balloon, rng, and optional EFI/SMM settings.

## Control Flow
`VmManager::create_vm` calls `generate_simple_vm_xml`, not the Tera renderer. UEFI mode changes the `<os>` section and adds `<smm state='on'/>`.

## State, Persistence, and Dependencies
The XML string becomes persistent only after libvirt `define_xml` stores the domain. The template renderer reads template files from disk. Dependencies include Tera, Serde, tracing, and path formatting.

## Risks and Test Signals
Direct string interpolation can produce invalid XML if VM names, paths, or network names contain special characters. The `network_name` argument is used as a libvirt network source, while surrounding config names it a bridge, which can cause deployment mismatch. Tests should parse generated XML for BIOS and UEFI cases and validate escaping or input restrictions.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/vm/xml.rs -->
