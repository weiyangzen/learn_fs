# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/accessors.c

Generated implementation for public accessors over libnvme topology and fabrics option structs.

Main behavior:
- Exports functions with `__libnvme_public`.
- Implements setters/getters for `libnvme_path`, `libnvme_ns`, `libnvme_ctrl`, `libnvme_subsystem`, `libnvme_host`, and `libnvme_fabric_options`.
- String setters free the old field and assign `strdup(new_value)` or `NULL`.
- Primitive setters assign directly.
- Getters return primitive values, borrowed string pointers, or borrowed array pointers.

Key object coverage:
- `libnvme_path`: name, sysfs directory, group ID.
- `libnvme_ns`: NSID, names, sysfs directory, LBA geometry/utilization, EUI64, NGUID, CSI.
- `libnvme_ctrl`: identity/sysfs strings, fabrics address fields, DH-CHAP keys, keyring/TLS fields, discovery state flags, persistence, and embedded `cfg` connection parameters.
- `libnvme_subsystem`: name/sysfs/NQN/model/serial/firmware/subsystem type and application ownership string.
- `libnvme_host`: host NQN/ID, DH-CHAP host key, symbolic host name.
- `libnvme_fabric_options`: booleans indicating which kernel fabrics options are supported.

Dependencies and integration:
- Includes `accessors.h`, `private.h`, and `compiler-attributes.h`.
- Reads and writes fields of private libnvme structs, providing controlled public access while keeping struct definitions opaque.
- Used broadly by tree, fabrics, JSON config, and discovery code.

Ownership and lifetime:
- Returned strings are internal borrowed pointers.
- Setters that use `strdup` do not report allocation failure; on allocation failure after freeing the previous value, the stored field becomes `NULL`.
- No NULL-object checks are performed; callers must pass valid object pointers.

Risks and tests:
- Since this is generated code, tests should focus on generator correctness and representative accessor behavior rather than hand-editing individual functions.
- Important cases: setter clears on NULL, string setters replace old values without leaks, and fabric option flags match `/dev/nvme-fabrics` option parsing.
