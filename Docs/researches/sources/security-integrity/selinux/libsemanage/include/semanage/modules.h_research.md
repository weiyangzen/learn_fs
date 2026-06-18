# sources/security-integrity/selinux/libsemanage/include/semanage/modules.h

Purpose: declares the public policy module management API for installing, removing, extracting, listing, enabling, and describing semanage modules.

Important APIs/types/functions: exports legacy install/remove/list/extract calls plus structured `semanage_module_info_t` and `semanage_module_key_t` create/destroy/get/set APIs. `semanage_module_install_info`, `get_module_info`, `list_all`, `set_enabled`, and `remove_key` support priority, module name, language extension, and enabled state.

Control flow: module operations are transaction-scoped. Callers create a key or info object, fill priority/name/lang/enabled fields, install raw module bytes or files, remove by name/key, extract mapped source or CIL bytes, and commit to compile/link/install the store.

State and persistence behavior: installs write module payloads under priority/name directories in the semanage module store, optionally compressed. Enable state is stored per module name across priorities. Extraction maps stored module data for the caller to unmap.

Dependencies and integration points: depends on `handle.h`, `stdint.h`, and `sys/types.h`; implemented mostly by `direct_api.c`; wrapped by SWIG; consumed by semodule-like tools and direct commit checksum logic.

Risks: ownership is mixed: info/key structs require destroy plus free, extracted blobs require `munmap`, and invalid modinfo can return distinct negative codes. Test signals include priority sorting, enable/disable across priorities, compressed module install/extract, invalid metadata rejection, and rebuild triggering on module changes.
