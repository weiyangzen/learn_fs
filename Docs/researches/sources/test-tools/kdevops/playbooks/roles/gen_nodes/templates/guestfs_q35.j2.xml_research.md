# Research: sources/test-tools/kdevops/playbooks/roles/gen_nodes/templates/guestfs_q35.j2.xml

`sources/test-tools/kdevops/playbooks/roles/gen_nodes/templates/guestfs_q35.j2.xml` is a template artifact in the kdevops `gen_nodes` role. Role context: generates libvirt guest node definitions and workflow-specific node metadata. The file is 195 lines / 7811 bytes and was read in full for this report.

## Purpose

This Jinja/XML template renders a libvirt domain definition for `gen_nodes` guest nodes. It contains XML elements `acpi`, `address`, `alias`, `apic`, `audio`, `backend`, `backingStore`, `boot`, `channel`, `clock`, `console`, `controller`, `cpu`, `currentMemory`, `devices`, `disk`, `domain`, `driver`, plus 25 more and Jinja expressions `hostname`, `libvirt_mem_mb`, `libvirt_mem_mb`, `libvirt_vcpus_count`, `'host-passthrough' if libvirt_host_passthrough else 'host-model'`, `qemu_bin_path`, `kdevops_storage_pool_path`, `hostname`, `libvirt_session_public_network_dev`, `guestfs_path`, `hostname`, `libvirt_gdb_baseport + idx`.

## Important APIs, Types, And Functions

Important rendered variables are `'host-passthrough'`, `guestfs_path`, `hostname`, `kdevops_storage_pool_path`, `libvirt_gdb_baseport + idx`, `libvirt_mem_mb`, `libvirt_session_public_network_dev`, `libvirt_vcpus_count`, `qemu_bin_path`. Jinja control blocks are `if guestfs_requires_uefi`, `else`, `endif`, `if libvirt_enable_gdb`, `endif`, `include './templates/gen_drives.j2'`. Structured tags/directives include `acpi`, `address`, `alias`, `apic`, `audio`, `backend`, `backingStore`, `boot`, `channel`, `clock`, `console`, `controller`, `cpu`, `currentMemory`, `devices`, `disk`, `domain`, `driver`, plus 25 more.

## Control Flow

Control flow is Jinja rendering: conditionals include or omit device/configuration blocks and loops expand disks, networks, PCIe passthrough, or service settings. The rendered artifact is then consumed by Ansible/libvirt or copied into service configuration by the parent role.

## State And Persistence

The template itself is stateless, but its rendered output becomes persistent VM XML, daemon configuration, or host policy. Those outputs can affect guest hardware topology, storage attachments, network behavior, TLS settings, or device permissions until regenerated or removed.

## Dependencies And Integration Points

It depends on variables supplied by the `gen_nodes` role, inventory, generated node metadata, and parent Ansible tasks. For libvirt XML, integration is with `community.libvirt.virt`/`virsh`; for daemon config, integration is with the corresponding system service.

## Risks And Edge Cases

Risks include undefined variables, invalid rendered XML/config syntax, host capability mismatches, and condition combinations that omit required devices or credentials. Template changes should be validated by rendering with representative inventories before applying to real hosts.

## Test Signals

Render with representative variable sets, validate XML/config syntax with the relevant tool (`virsh define --validate` or daemon config checks), and confirm the parent Ansible task consumes the rendered file successfully.
