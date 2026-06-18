# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/util-fabrics.c

## Purpose
NVMe-oF fabrics utility implementation for extended attributes, interface caching, and host entity metadata strings.

## Main Logic
- `libnvmf_exat_ptr_next()` advances over variable-sized `struct nvmf_ext_attr` records using encoded extended-attribute length.
- `libnvmf_getifaddrs()` lazily caches `getifaddrs()` results in the global context.
- `libnvmf_get_entity_name()` returns the local hostname in a zero-filled buffer.
- `libnvmf_get_entity_version()` builds a version string from `/proc/sys/kernel/ostype`, `/proc/sys/kernel/osrelease`, and `NAME`/`VERSION_ID` in `/etc/os-release`.

## Parsing Details
Local helpers strip trailing whitespace/newlines, strip quotes around os-release values, and copy bounded values into caller buffers.

## Relevance
Supports fabrics discovery-controller metadata and host-interface matching infrastructure used by NVMe-oF connection and discovery flows.
