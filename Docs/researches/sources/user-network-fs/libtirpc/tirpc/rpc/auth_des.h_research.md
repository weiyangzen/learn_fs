# sources/user-network-fs/libtirpc/tirpc/rpc/auth_des.h

Purpose: `auth_des.h` defines the wire structures for legacy DES/Diffie-Hellman RPC authentication.

Important APIs, types, and functions: It defines `enum authdes_namekind`, `struct authdes_fullname`, `struct authdes_cred`, `struct authdes_verf`, verifier field aliases such as `adv_timestamp` and `adv_nickname`, and prototypes `rtime` and `kgetnetname`.

Control flow: DES credentials are either full names with client netname, conversation key, and window, or server-assigned nicknames. Verifiers carry encrypted timestamps/window verification or server nickname/time verification depending on direction.

State and persistence behavior: The header declares only caller-owned credential/verifier structures. Runtime nickname caches, time sync, and key material are managed by implementation files.

Dependencies and integration points: It includes `rpc/auth.h` for `des_block`, `MAXNETNAMELEN`, and auth flavor constants. `authdes_create` declarations live in `auth.h`; generated key protocol headers also share DES block types.

Risks: DES authentication is cryptographically obsolete and depends on time synchronization and keyserv behavior. The use of `u_int32_t` in places where historical APIs used `u_long` is ABI-sensitive. Time windows and nicknames can be replay-sensitive if implementation checks are weak.

Test signals: Tests should cover XDR round trips for full-name and nickname credentials, timestamp/window verifier construction, time sync fallback, and interoperability with legacy AUTH_DES peers where still supported.
