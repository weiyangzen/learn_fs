# sources/user-network-fs/samba/source4/param/share_classic.c

Purpose: `share_classic.c` implements the `classic` share backend by adapting Samba loadparm services to the generic share API.

Important APIs, types, and functions: Key functions are `sclassic_init`, `sclassic_string_option`, `sclassic_int_option`, `sclassic_bool_option`, `sclassic_string_list_option`, `sclassic_list_all`, `sclassic_get_config`, static `ops`, and `share_classic_init`.

Control flow: Initialization stores the loadparm context as backend private data. Option getters check for parametric `type:option` names first, then map generic share option names to loadparm service getters and defaults. Listing iterates all configured services. `get_config` looks up a service by name and returns a `share_config` with opaque service pointer. The ops table omits create/set/remove, making mutations unsupported.

State and persistence behavior: The backend references the existing loadparm context; it does not write configuration. Returned share configs are talloc objects that point back to loadparm service structures.

Dependencies and integration points: It depends on loadparm service APIs and `share_register`. NTVFS connect code consumes `SHARE_PATH`, read-only, mask, oplock, case, and parametric options through this backend.

Risks: Unknown options log and return defaults, which can hide configuration mistakes. Parametric integer options treat zero as missing and replace it with the default. The case-insensitive filesystem mapping is intentionally nuanced and easy to misread.

Test signals: Local share tests cover context setup and unsupported create/remove paths. Additional tests should cover every mapped option, parametric strings/ints/bools/lists, unknown share lookup, and zero-valued parametric integer behavior.
