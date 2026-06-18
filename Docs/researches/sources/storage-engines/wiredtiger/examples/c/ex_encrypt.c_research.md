# sources/storage-engines/wiredtiger/examples/c/ex_encrypt.c

Purpose: implements and exercises a local rotate-N encryptor extension, including encrypted logs, per-table encryption configuration, custom key IDs, and restart verification.

Important APIs and control flow: `MY_CRYPTO` embeds `WT_ENCRYPTOR` first and tracks rotation, calls, key ID, and password. `rotate_encrypt` reserves checksum/IV header space, copies input, applies `do_rotate`, writes fixed checksum/IV bytes, and reports expansion. `rotate_decrypt` strips header and reverses rotation. `rotate_sizing`, `rotate_customize`, and `rotate_terminate` implement sizing, per-object customization via `keyid`/`secretkey`, and cleanup. `add_my_encryptors` registers `rotn` through `connection->add_encryptor`. `main` opens with `extensions=[local=(entry=add_my_encryptors)]`, writes/read-walks encrypted log records, creates encrypted and unencrypted tables, verifies bad key ID failure, inserts identical rows into all tables, closes/reopens, and verifies decrypted table/log reads match.

State and persistence: persists encrypted table files and encrypted logs in WT_HOME. Customized encryptors hold allocated key/password strings until termination. Restart forces disk reads and decryption.

Dependencies and integration: requires `-rdynamic`/local extension symbol visibility, logging, WiredTiger encryption hooks, and `test_util.h`.

Risks: checksum and IV are fixed placeholders and not secure. `rotate_encrypt` sets `*result_lenp = dst_len` rather than the actual used `src_len + CHKSUM_LEN + IV_LEN`, acceptable only as demo behavior if buffers are sized exactly. Key management is illustrative.

Test signals: unknown key ID must fail, log cursor must find messages before and after restart, and all encrypted/unencrypted table cursors must return identical keys and values.
