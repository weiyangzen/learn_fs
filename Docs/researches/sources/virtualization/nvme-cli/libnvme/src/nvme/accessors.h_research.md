# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/accessors.h

Generated public declaration header for libnvme topology and fabrics option accessors.

Main API surface:
- Forward-declares opaque structs: `libnvme_path`, `libnvme_ns`, `libnvme_ctrl`, `libnvme_subsystem`, `libnvme_host`, and `libnvme_fabric_options`.
- Declares path accessors for device/sysfs names and group ID.
- Declares namespace accessors for NSID, names, sysfs directory, LBA sizes/counts, EUI64, NGUID, and command set identifier.
- Declares controller accessors for sysfs/identity fields, address/transport fields, DH-CHAP/TLS/keyring fields, discovery flags, persistence, and connection config fields.
- Declares subsystem and host accessors for static identity plus mutable application/crypto/symbolic fields.
- Declares per-option booleans in `libnvme_fabric_options`.

Dependencies and integration:
- Includes standard bool/int headers and `<nvme/types.h>`, `<nvme/nvme-types.h>`.
- Matched by generated implementations in `accessors.c`.
- Allows external callers to inspect libnvme tree objects without depending on private struct layouts.

Ownership contract:
- Documentation distinguishes copied string setters from borrowed-pointer getters.
- EUI64 and NGUID getters return pointers to fixed internal arrays.
- Fabric option setters/getters are simple boolean controls.

Risks and notes:
- The generated API has no runtime validation or allocation-error reporting in the setter signatures.
- Callers must treat returned pointers as valid only while the owning libnvme object is alive and unchanged.
- Any new private field that should be public must be added through the accessor generator, not by manually editing this file.
