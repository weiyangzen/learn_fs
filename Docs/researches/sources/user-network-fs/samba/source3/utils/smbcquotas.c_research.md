# sources/user-network-fs/samba/source3/utils/smbcquotas.c

`smbcquotas.c` implements the `smbcquotas` utility for querying and setting NT quota information on SMB shares. It supports filesystem quota defaults, user quota listing, single-user quota query, user limit setting, filesystem limit setting, and filesystem quota flag setting.

Key functions are `parse_quota_set`, `dump_ntquota`, `dump_ntquota_list`, `do_quota`, `SidToString`, `StringToSid`, `cli_open_policy_hnd`, and `connect_one`. `parse_quota_set` recognizes `UQLIM:`, `FSQLIM:`, and `FSQFLAGS:` strings. `do_quota` checks filesystem quota support, opens the quota fake file, and calls `cli_get_user_quota`, `cli_list_user_quota`, `cli_set_user_quota`, `cli_get_fs_quota_info`, or `cli_set_fs_quota_info`.

`main` parses mutually exclusive operation options, defaults to the authenticated username for user quota queries, validates `//server/share`, splits server/share, parses set strings, connects, and dispatches. Persistent state changes are remote quota records and filesystem quota settings.

Dependencies include Samba client connections, LSA RPC over IPC$ for SID/name translation, fake quota file helpers, credentials, and loadparm. Risks include in-place mutation of set strings, global IPC/LSA state tied to parsed `server`, server/filesystem quota variability, and subtle quota flag precedence. Test signals: all set syntaxes, invalid options, unsupported quotas, numeric output, user get/list/set, filesystem limits/flags, and `--test-args`.
