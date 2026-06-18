# sources/test-tools/kdevops/scripts/workflows/cxl/gen_qemu_cxl.py

## Purpose
Generates QEMU command-line or libvirt XML `qemu:arg` fragments for CXL topologies.

## Important APIs
Builder functions produce device/object strings: `host_bridge()`, `root_port()`, `switch()`, `mailbox()`, `downstream_port()`, `memdev()`, `lsa()`, `type3()`, and `fmw()`. `qemu_print(kind, value, last=False)` emits either command-line continuation syntax or XML.

## Control flow
After argument parsing, the script validates size suffix `M` or `G`, computes bytes, emits `-machine cxl=on`, creates or references an LSA file, loops over host bridges, root ports, switches, downstream ports, memory backend files, and type3 devices, then emits a fixed-window memory mapping.

## State and persistence
With `--create-memdev-files`, it creates sparse raw files under `--memdev-path`: one `cxl_lsa.raw` and one `cxl_mem<N>.raw` per downstream port. It uses `os.umask(0)` before file creation.

## Dependencies and integration
Uses Python standard library only. Integrates with QEMU/libvirt launch configuration for CXL test workflows.

## Risks and test signals
The script exits if the backing directory is missing and does not validate free space. Global `args` is referenced by `qemu_print`. Test by generating both formats with small topologies and verifying QEMU accepts the emitted topology.
