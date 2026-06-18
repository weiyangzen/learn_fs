# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/space.c

Holds resident kernel data and a small persistent key/value pointer registry. The file centralizes globals that must remain loaded in the kernel.

Resident globals:
- Buffer and VM/system accounting: `bfreelist`, `sysinfo`, `vminfo`.
- Physical memory descriptors: `physmax`, `physinstalled`.
- Kernel vnode page storage: `kvps[KV_MAX]`.
- Root device state: `rootvp`, `rootdev`, `root_is_ramdisk`, `ramdisk_size`.
- Netboot/DHCP state: `netboot`, `obpdebug`, `dhcack`, `dhcacklen`, `netdev_path`, `dhcifname`.
- Network constant: `etherbroadcastaddr`.
- Console/input device state: keyboard, mouse, stdin, diagnostic, framebuffer, workstation console, real console, user console, serial virtual console, abort policy, and terminal-emulator mode.
- CPC key: `kcpc_key`.
- CRC support: `crc32_table`.
- MAC soft ring default: `mac_soft_ring_enable`.
- iSCSI boot property pointer: `iscsiboot_prop`.

Initialization:
- `space_init()` initializes PTY resident data and the store/fetch hash.
- `store_fetch_initspace()` creates `space_hash`, a string-keyed `mod_hash`.

Persistent pointer registry:
- `space_store()` validates a non-empty key, copies the string, and inserts a `uintptr_t` value. Duplicate or allocation errors return `-1`; debug builds log details.
- `space_fetch()` returns the stored pointer value or zero.
- `space_free()` removes the key from the hash.
- Comments recommend this mechanism for module data that must survive unload/load cycles instead of adding more globals to this file.

Filesystem relevance:
- Contains direct VFS-adjacent state: `rootvp`, `rootdev`, resident vnode storage, console vnodes, and boot device metadata.
- The persistent pointer registry can be used by modules, including filesystem/storage modules, to retain kernel-resident data across reloads.
