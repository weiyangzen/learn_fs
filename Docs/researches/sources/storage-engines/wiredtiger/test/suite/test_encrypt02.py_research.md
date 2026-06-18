# sources/storage-engines/wiredtiger/test/suite/test_encrypt02.py

Purpose: tests encryption configured with secret/password arguments and verifies `wt` utility access with `-E`.

Important APIs and control flow: scenarios cover rotn with no key ID, key ID, secret key, key ID plus secret, and sodium with a hex secret. `conn_extensions` loads rotn and sodium. `conn_config` builds system encryption with optional `secretkey`. The test creates an encrypted file, writes deterministic random records, reopens and verifies them, then runs `wt dump`, adding `-E <secret>` when needed.

State and persistence: encrypted pages must survive reopen and be readable by both library and command-line utility.

Dependencies and integration: uses `suite_subprocess`, encryptor extensions, sodium secret key, random deterministic data, and utility dump.

Risks and test signals: detects secret propagation errors, key ID handling regressions, and utility failure to open encrypted homes.
