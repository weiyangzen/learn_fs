# sources/user-network-fs/samba/source3/script/tests/test_smbcquota.py

## Purpose
This Python blackbox test verifies `smbcquotas` list, get, and set behavior against a selftest quota directory backed by a simple quota database and helper script.

## Important APIs, Types, Functions, and Control Flow
Classes `test_env`, `user_info`, and `Quota` store environment, passwd user data, and quota rows. Helpers include `init_quota_db`, `load_quotas`, `get_quotas`, `get_users`, `smbcquota_output_to_userinfo`, `check_quota_limits`, and `get_uid`. Test classes `listtest`, `gettest`, and `settest` inherit `test_base` and implement `run(protocol)`. `main` parses `server domain username password envdir smbcquotas`, copies sibling `getset_quota.py` into the environment directory, builds `quotas.db` from local passwd users, then runs every subtest for `smb1` and `smb2`.

## State, Dependencies, Integration, and Risks
The test writes `quotas.db` and copies `getset_quota.py` into the supplied envdir. It depends on `getent passwd`, the `quotadir` share, the quota helper script, and `smbcquotas` output format. A code risk is that `listtest` prepares an `args` list with protocol but then invokes a hard-coded command that ignores the protocol-specific `-m smb2`, so SMB2 coverage may be weaker than intended. Test signals are parsed quota limits matching defaults or updated limits, with process exit 1 on first failure.
