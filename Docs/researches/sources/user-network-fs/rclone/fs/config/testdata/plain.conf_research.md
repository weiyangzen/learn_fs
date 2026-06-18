<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/testdata/plain.conf -->
# sources/user-network-fs/rclone/fs/config/testdata/plain.conf

## Purpose
Plaintext config fixture representing the decrypted content expected from the encrypted fixture.

## Important APIs, Types, And Control Flow
Defines a `RCLONE_ENCRYPT_V0` local section plus `nounc` and `unc` local remotes with boolean `nounc` values. It provides a readable baseline for config parser behavior and encrypted fixture semantics.

## State And Persistence
Static INI-style config data with no mutation.

## Dependencies And Integration Points
May be used by config load tests and as human-readable companion data for encrypted config tests.

## Risks And Test Signals
Validates simple section/key parsing shape. It does not include comments, duplicate keys, escaped values, or password fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/testdata/plain.conf -->
