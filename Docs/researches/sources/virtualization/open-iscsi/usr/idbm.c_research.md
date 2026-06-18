# File Research: sources/virtualization/open-iscsi/usr/idbm.c

Core iSCSI discovery database manager. It owns conversion between in-memory records and the on-disk open-iscsi database under node, discovery, static, firmware, and iSNS directories.

The first major layer builds `recinfo_t` arrays for discovery records, node records, iface records, host CHAP records, and flashnode records. Macros populate typed fields, current string values, backing data pointers, visibility, valid options, and mutability. Sensitive password values are marked masked for printing. CHAP algorithm lists support MD5, SHA1, SHA256, and conditionally SHA3-256.

Printing uses `idbm_print()` to emit `ISCSI_BEGIN_REC` / `ISCSI_END_REC` records, optionally masking passwords. Config parsing in `idbm_recinfo_config()` reads `name = value` lines, strips comments/blank lines, warns about malformed or overlong lines, and updates recinfo-backed structures through `idbm_rec_update_param()`.

Parameter update logic supports integer, uint8/16/32, string, enumerated integer options, and integer-list options. It also auto-updates password length fields when password fields change. `idbm_verify_param()` blocks modification of identity fields used to locate records.

Default setup covers discovery defaults, session operational defaults, connection operational defaults, and full node defaults. Defaults include startup policy, login/reopen timers, command limits, queue depth, CHAP defaults, digest settings, connection timeouts, and iface defaults. `idbm_sync_config()` overlays defaults from the global config file when available.

Persistence supports old and new database layouts. Node records may be stored as old-style portal files or new-style target/portal/tpgt/iface paths. Write paths create missing directories, convert old portal files into directories when needed, and preserve backward compatibility. Discovery records are stored under sendtargets or iSNS roots and also support old file-vs-directory formats.

Iteration helpers traverse discovery records, target nodes, portals, and iface-bound records. They expose callback-based enumeration for printing, updating, and matching. Discovery printing groups sendtargets, iSNS, static, and firmware records, with compatibility logic for older iSNS layouts.

Locking uses a global `db` object with recursive reference counting and a hard-link based write lock under `LOCK_DIR`. It retries for up to `DB_LOCK_RETRIES` with `DB_LOCK_USECS_WAIT` sleeps, then removes `LOCK_WRITE_FILE` on unlock.

Discovery-to-node relationships are represented by symlinks. `setup_disc_to_node_link()` computes link paths for sendtargets, firmware, static, and iSNS records, including old iSNS compatibility. Add/delete paths create or remove these links while writing/removing node records.

`idbm_add_node()` optionally overwrites existing records, applies discovery metadata, marks firmware-discovered nodes as onboot, writes the node, and creates discovery links when TPGT is known. `idbm_delete_node()` removes discovery links, node config files, empty portal directories, and empty target directories. `idbm_delete_discovery()` removes discovery config and associated node links.

The file also provides user parameter allocation/free helpers, node/discovery parameter setters, default-copy helpers for sendtargets and iSNS, session autoscan lookup, database init/terminate, record creation from explicit parameters, record creation from firmware boot context, and list search by session identity.

Notable risks: path construction relies heavily on fixed `PATH_MAX` buffers and formatted strings; many paths assume global `db` has been initialized; some compatibility branches can continue after partial cleanup failures; and record file parsing is permissive, warning and continuing on malformed lines.
