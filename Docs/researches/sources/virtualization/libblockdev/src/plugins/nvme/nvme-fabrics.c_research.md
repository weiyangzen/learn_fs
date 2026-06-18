# File Research: sources/virtualization/libblockdev/src/plugins/nvme/nvme-fabrics.c

## Purpose

Implements the NVMe over Fabrics initiator-facing API for the libblockdev NVMe plugin. It wraps libnvme discovery/config/topology calls for connecting, disconnecting, matching sysfs controllers/namespaces, and managing global host NQN/host ID files.

## Main Responsibilities

- Parse `BDExtraArg` connection options into `struct nvme_fabrics_config`.
- Establish Fabrics controllers through libnvme host/controller objects.
- Disconnect controllers by subsystem NQN or controller device name.
- Find controllers associated with a namespace sysfs path.
- Find namespaces associated with a controller sysfs path.
- Read, generate, and write host NQN and host ID values.

## Important Functions

- `parse_extra_args()` accepts string options such as `config`, DH-HMAC-CHAP keys, queue counts, timeouts, TCP digest flags, TLS flags, host symbolic name, and libnvme 1.4 keyring/TLS key settings.
- `bd_nvme_connect()` validates required parameters, derives missing host NQN/host ID, reads the optional config file, creates a libnvme controller, and calls `nvmf_add_ctrl()`.
- `_disconnect()` scans live topology and disconnects matching controllers.
- `bd_nvme_disconnect()` removes all controllers matching a subsystem NQN.
- `bd_nvme_disconnect_by_path()` strips `/dev/` and removes a matching controller name.
- `bd_nvme_find_ctrls_for_ns()` scans libnvme topology and returns real sysfs controller paths connected to or sharing the requested namespace.
- `bd_nvme_find_namespaces_for_ctrl()` returns namespace sysfs paths under a matching controller plus subsystem-level namespaces.
- `bd_nvme_get_host_nqn()`, `bd_nvme_generate_host_nqn()`, `bd_nvme_get_host_id()`, `bd_nvme_set_host_nqn()`, and `bd_nvme_set_host_id()` manage host identity values.

## Dependencies and Interactions

- Uses libnvme topology APIs: `nvme_scan()`, `nvme_lookup_host()`, `nvme_create_ctrl()`, `nvmf_add_ctrl()`, `nvme_scan_topology()`, `nvme_disconnect_ctrl()`.
- Uses libnvme host identity helpers: `nvmf_hostnqn_from_file()`, `nvmf_hostid_from_file()`, `nvmf_hostnqn_generate()`.
- Uses shared NVMe error helpers from `nvme-private.h`.
- Writes host files under `PACKAGE_SYSCONF_DIR/nvme`, while comments note libnvme may use a different compiled `SYSCONFDIR`.

## Notable Details

- Default config file is `/etc/nvme/config.json`; `extra` option `config=none` disables config-file loading.
- If `transport_svcid` is omitted, TCP discovery uses the discovery port and TCP non-discovery currently falls through to the RDMA default port constant.
- Host ID can be derived from `uuid:` embedded in the host NQN when `/etc/nvme/hostid` is missing.
- Sysfs matching uses `realpath()` before comparing paths.
- The sysfs lookup functions ignore their `error` parameter and return an allocated, NULL-terminated array even if no match is found.
