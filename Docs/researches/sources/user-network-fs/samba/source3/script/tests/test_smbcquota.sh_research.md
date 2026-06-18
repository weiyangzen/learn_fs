# sources/user-network-fs/samba/source3/script/tests/test_smbcquota.sh

## Purpose
This shell wrapper runs the Python `test_smbcquota.py` suite under Samba selftest/subunit conventions.

## Important APIs, Functions, and Control Flow
It accepts `SERVER DOMAIN USERNAME PASSWORD LOCAL_PATH SMBCQUOTAS`, derives `ENVDIR=$(dirname $5)`, wraps `SMBCQUOTAS` with `$VALGRIND`, locates `test_smbcquota.py` next to itself, loads `subunit.sh`, and runs one `testit "smbcquotas"` command passing server, domain, credentials, envdir, and smbcquotas path.

## State, Dependencies, Integration, and Risks
The wrapper itself writes nothing, but delegates envdir mutation to the Python test. It depends on the Python script being executable and in the same directory. It increments `failed` without explicit initialization, relying on shell behavior. The test signal is the Python exit code reported as a single subunit test plus final `testok`.
