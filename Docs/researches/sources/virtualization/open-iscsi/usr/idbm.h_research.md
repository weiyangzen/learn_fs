# File Research: sources/virtualization/open-iscsi/usr/idbm.h

This header defines the public interface for open-iscsi's initiator database manager, which persists and retrieves discovery, node, iface, host CHAP, and flashnode records below `ISCSI_DB_ROOT`.

Key contents:
- Database path constants for nodes, iSNS, static, firmware, and SendTargets records: `NODE_CONFIG_DIR`, `ISNS_CONFIG_DIR`, `STATIC_CONFIG_DIR`, `FW_CONFIG_DIR`, `ST_CONFIG_DIR`.
- Record value typing constants used by `recinfo_t`: integer, string, sized integer, and integer-list variants.
- `recinfo_t`, the generic descriptor for a configurable key: name, value string, backing data pointer/length, visibility, accepted options, and mutability.
- `idbm_t`, the in-memory database manager state, holding config file callback, node/discovery defaults, and `recinfo_t` arrays.
- `struct user_param`, a list item for user-supplied name/value updates.
- Iteration callback types and walkers for portals, nodes, node records, SendTargets discovery records, and iSNS discovery records.
- CRUD/default/read/update/print APIs for node records, discovery records, iface records, host CHAP records, and flashnode records.
- Lower-level helpers exported for `iface.c`, including config serialization/parsing, record metadata construction, DB locking, parameter verification, and parameter update.

Important dependencies:
- Includes `initiator.h`, `config.h`, `list.h`, and `flashnode.h`.
- The header exposes `node_rec_t`, `discovery_rec_t`, `struct iface_rec`, `struct iscsi_chap_rec`, and `struct flashnode_rec` interactions, so it is a central bridge between persisted config and runtime initiator/session structures.

Filesystem/storage relevance:
- This is the control-plane persistence layer for iSCSI storage targets. It does not issue I/O itself, but it defines the records that determine which remote block devices are discovered, logged into, scanned, and exposed to the host.

Notable implementation constraints:
- Fixed maxima are used for keys, key names, values, and option lists (`MAX_KEYS`, `NAME_MAXVAL`, `VALUE_MAXVAL`, `OPTS_MAXVAL`).
- DB locking policy is exposed with retry timing constants and lock/unlock functions.
- There is a duplicated declaration of `idbm_node_setup_defaults`.
