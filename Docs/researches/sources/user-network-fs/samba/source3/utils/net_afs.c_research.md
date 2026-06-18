# sources/user-network-fs/samba/source3/utils/net_afs.c

Purpose: implements optional `net afs` commands for fake KASERVER/OpenAFS support when `WITH_FAKE_KASERVER` is enabled.

Important APIs/types/functions: `net_afs()` dispatches `key` and `impersonate`; `net_afs_key()` imports an OpenAFS `KeyFile` into Samba secrets; `net_afs_impersonate()` creates and installs a token; `net_afs_usage()` prints help.

Control flow: key import validates two arguments, initializes `secrets.tdb`, opens and reads a fixed-size `struct afs_keyfile`, stores it with `secrets_store_afs_keyfile()`, and zeros the key buffer. Impersonation validates user/cell, calls `afs_createtoken_str()` then `afs_settoken_str()`, and prints success.

State and persistence: `key` persists AFS key material in `secrets.tdb`; `impersonate` writes token state into the kernel AFS token facility.

Dependencies/integration: depends on AFS helper libraries, `secrets.h`, filesystem APIs, `utils/net_afs.h`, and generic `net_run_function()` dispatch.

Risks: compiled out unless the feature is enabled. `net_afs_impersonate()` calls `exit(1)` on failures instead of returning. Keyfile import assumes exact structure layout. Secret material must remain zeroed across all paths.

Test signals: feature-enabled/disabled builds; valid/truncated/missing keyfile import; secrets lookup by cell; token creation/set failures; usage output.
