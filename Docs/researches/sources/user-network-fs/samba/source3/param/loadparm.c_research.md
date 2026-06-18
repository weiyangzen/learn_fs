# sources/user-network-fs/samba/source3/param/loadparm.c

Purpose: this is the Samba3 configuration engine. It initializes global and share defaults, parses smb.conf/registry configuration, creates and hashes service records, exposes `lp_*` accessors, handles parametric options, loads usershares, tracks config-file changes, and enforces derived security/server-role settings.

Important APIs and types: central state is `Globals`, `sDefault`, `ServicePtrs`, `ServiceHash`, `flags_list`, `file_lists`, and `stored_options`. Public APIs include `loadparm_s3_init_globals()`, `store_lp_set_cmdline()`, `lp_do_parameter()`, `lp_do_section()`, `lp_load_*()` wrappers, `lp_servicenumber()`, `lp_add_home()`, `lp_add_printer()`, `load_usershare_service()`, `load_usershare_shares()`, `parse_usershare_file()`, `lp_parm_*()` parametric readers, canonicalization helpers, dump helpers, and derived getters such as `lp_server_role()`, `lp_security()`, `lp_widelinks()`, and `lp_server_smb_encrypt()`.

Control flow: `lp_load_ex()` resets parse state, initializes globals, parses file or registry backends, processes shares, auto-loads home services, optionally adds IPC/Admin shares, clamps client auth, initializes iconv, enforces AD DC settings, and validates min/max protocol. Section callbacks validate the previous service before adding the next. Registry inclusion is guarded by include depth and only effective from globals.

State and persistence: persistent inputs are smb.conf files, registry smbconf, usershare files, share-security TDB, and system state paths. Runtime state is global and mutable; command-line options are stored and re-applied across reloads. File modification tracking stores original and substituted include paths plus mtimes.

Dependencies and integration: integrates lib/param generated tables, smbconf, dbwrap rbt hash, talloc, printing defaults, idmap parametrics, charset/iconv, auth/credentials, server role logic, usershare ACL/security helpers, and smbd callbacks for in-use service numbers.

Risks: highly stateful global parser with reload paths, recursive include handling, registry/file backend switching, and service deletion while smbd may hold active connections. Usershare loading is security-critical and depends on lstat/open/fstat race checks, directory ownership/sticky-bit policy, path allow/deny lists, ACL parsing, and share count limits. A notable edge in `load_usershare_shares()` counts a successfully loaded usershare only when `process_usershare_file()` returns `0`, although service numbers are generally nonnegative and may not be zero. Parameter flags and synonyms must stay aligned with generated `parm_table`.

Test signals: repeated `lp_load_with_registry_shares()` runs, config reload detection, param canonicalization/value validation, registry include/backend switch, usershare symlink/race/path/ACL cases, AD DC enforced defaults, min/max protocol warnings, and dynamic service cleanup with in-use callbacks.
