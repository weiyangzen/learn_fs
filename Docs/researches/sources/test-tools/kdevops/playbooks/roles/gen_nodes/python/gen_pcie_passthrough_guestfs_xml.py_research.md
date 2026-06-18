# sources/test-tools/kdevops/playbooks/roles/gen_nodes/python/gen_pcie_passthrough_guestfs_xml.py

## Purpose
Python helper for generating libvirt guest XML fragments for PCIe passthrough. It converts declarative host/device arguments into a guestfs-compatible XML device stanza.

## Important APIs, Types, and Functions
Python functions include `main`. The role-level integration surface is the `gen_nodes` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
The helper parses command-line arguments, builds an XML tree for PCI host-device passthrough, derives domain/bus/slot/function addresses, and prints/writes the generated XML for the caller.

## State and Persistence Behavior
The file mutates target or localhost state through none detected. Notable path references include `/extra_vars.yaml`, `/hostdev`, `/source`, `/usr/bin/python3`, `/{extra_vars`, `/{name}/pcie_passthrough_`. Registered results and facts are transient Ansible state, while package installs, service enablement, generated configs, repositories, mounts, fetched results, and generated inventories persist outside the playbook run.

## Dependencies and Integration Points
Integrated before provisioning. It consumes workflow enablement variables, cloud/guestfs/NixOS settings, filesystem test choices, PCI passthrough inputs, and emits node lists or templates consumed by Terraform/libvirt/Ansible.

## Risks
The main risks are incorrect node-count/list expansion, provider template mismatches, PCI address formatting, and generated node files becoming inconsistent with inventory templates.

## Test Signals
Useful test signals include run the helper with representative PCI addresses; parse the emitted XML; validate the generated XML with libvirt tooling.
