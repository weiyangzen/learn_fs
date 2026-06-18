# File Research: sources/virtualization/spdk/lib/init/subsystem_rpc.c

`subsystem_rpc.c` implements runtime framework RPCs for subsystem and PCI introspection.

`framework_get_subsystems` takes no parameters and returns an array of registered subsystems, each with its name and a `depends_on` array derived from dependency records.

`framework_get_config` decodes a subsystem name and optional `with_batches` flag, looks up the subsystem, and writes its saved configuration through `subsystem_config_json()`. When `with_batches` is false, it adds the JSON writer flag to flatten batches.

`framework_get_pci_devices` takes no parameters and returns all SPDK PCI devices. Each entry includes formatted BDF address, device type, NUMA ID, and PCI config space as a byte array. It reads the first 256 bytes and includes extended config space only when the extended region is not all zeroes.

Research notes: these are control-plane inspection RPCs registered for `SPDK_RPC_RUNTIME`. They depend on generated RPC decode/free helpers for `framework_get_config`.
