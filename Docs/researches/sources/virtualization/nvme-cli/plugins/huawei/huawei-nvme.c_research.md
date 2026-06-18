# File Research: sources/virtualization/nvme-cli/plugins/huawei/huawei-nvme.c

- Purpose: Huawei vendor plugin for listing Huawei NVMe namespaces and decoding Huawei identify-controller vendor data.
- Device scan: scans `/dev` with `libnvme_filter_namespace`, opens namespace devices, identifies controller and namespace, and filters by model containing `Huawei` or PCI vendor ID `0x19E5`.
- List data: records device node, namespace ID, block-device status, namespace vendor name, array vendor name, NGUID, and usage computed from LBA size and namespace utilization.
- Output: prints aligned normal table or JSON device array with device path, index, namespace name, and array name.
- Identify support: `huawei_id_ctrl` delegates to `__id_ctrl()` and decodes the vendor-specific array name.
- Notable issue: length helper loops use `list_items->ns_name` and `list_items->array_name` instead of indexing `list_items[i]`, so computed column widths may only reflect the first item.
