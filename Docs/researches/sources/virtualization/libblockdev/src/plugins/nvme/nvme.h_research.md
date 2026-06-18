# File Research: sources/virtualization/libblockdev/src/plugins/nvme/nvme.h

## Purpose

Public API header for the libblockdev NVMe plugin.

## Main API Surface

- Error domain:
  - `bd_nvme_error_quark()`
  - `BDNVMEError`
- Technology categories:
  - `BD_NVME_TECH_NVME`
  - `BD_NVME_TECH_FABRICS`
  - info, manage, and initiator modes.
- Controller reporting:
  - `BDNVMEControllerFeature`
  - `BDNVMEControllerType`
  - `BDNVMEControllerInfo`
- Namespace reporting:
  - `BDNVMELBAFormat`
  - `BDNVMENamespaceFeature`
  - `BDNVMENamespaceInfo`
- Health/log reporting:
  - `BDNVMESmartLog`
  - `BDNVMEErrorLogEntry`
  - `BDNVMESelfTestLog`
  - `BDNVMESanitizeLog`
- Operations:
  - self-test, format, sanitize.
- Fabrics:
  - host NQN/ID management,
  - connect/disconnect,
  - namespace/controller sysfs lookup helpers.

## Important Functions Declared

- Lifecycle and availability:
  - `bd_nvme_init()`
  - `bd_nvme_close()`
  - `bd_nvme_is_tech_avail()`
- Info queries:
  - `bd_nvme_get_controller_info()`
  - `bd_nvme_get_namespace_info()`
  - `bd_nvme_get_smart_log()`
  - `bd_nvme_get_error_log_entries()`
  - `bd_nvme_get_self_test_log()`
  - `bd_nvme_get_sanitize_log()`
- Management:
  - `bd_nvme_device_self_test()`
  - `bd_nvme_format()`
  - `bd_nvme_sanitize()`
- Fabrics:
  - `bd_nvme_get_host_nqn()`
  - `bd_nvme_generate_host_nqn()`
  - `bd_nvme_get_host_id()`
  - `bd_nvme_set_host_nqn()`
  - `bd_nvme_set_host_id()`
  - `bd_nvme_connect()`
  - `bd_nvme_disconnect()`
  - `bd_nvme_disconnect_by_path()`
  - `bd_nvme_find_ctrls_for_ns()`
  - `bd_nvme_find_namespaces_for_ctrl()`

## Dependencies and Interactions

- Uses GLib/GObject types and `BDExtraArg` from blockdev utils.
- Structs are paired with copy/free helpers for introspection bindings and callers that need ownership-safe data handling.

## Notable Details

- The header documents destructive behavior for format and sanitize operations.
- `BD_NVME_SANITIZE_STATUS_IN_PROGESS` is retained as a deprecated misspelled alias for `BD_NVME_SANITIZE_STATUS_IN_PROGRESS`.
- Error values include both generic NVMe status categories and NVMe Fabrics connection failures.
