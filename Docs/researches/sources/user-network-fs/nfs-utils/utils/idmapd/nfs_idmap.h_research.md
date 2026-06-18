# sources/user-network-fs/nfs-utils/utils/idmapd/nfs_idmap.h

Purpose: defines the fixed kernel/userspace binary message format for client-side idmapping.

Important APIs and types: `struct idmap_msg` contains `im_type`, `im_conv`, `im_name[IDMAP_NAMESZ]`, `im_id`, and `im_status`. Constants define user/group types, id-to-name/name-to-id conversions, status bits, name size, and max message size.

Control flow and integration: `idmapd.c` reads and writes exactly this struct on client rpc_pipefs `idmap` files in `nfscb()`. The same constants drive conversion dispatch and result status handling.

State and persistence: no state; it is an ABI-style header mirrored from Linux NFS idmap expectations.

Dependencies: uses fixed-width integer typedefs expected from system headers included by the consumer.

Risks: field size/order is a compatibility contract with the kernel; changes would break binary pipefs communication. `IDMAP_NAMESZ` constrains owner/group string lengths. Test signals include struct size compatibility, round-trip binary reads/writes, lookup failure status handling, and bounds around 127-character names.
