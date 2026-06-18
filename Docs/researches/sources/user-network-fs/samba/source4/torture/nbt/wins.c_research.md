
# sources/user-network-fs/samba/source4/torture/nbt/wins.c

## Purpose
`wins.c` implements functional WINS server torture tests. It registers, queries, refreshes, releases, and re-queries many NetBIOS name variants to validate WINS semantics, conflict behavior, group-name behavior, case sensitivity, scope handling, long-scope limits, and security around names passed to the WINS hook.

## Important APIs, Types, And Functions
Macros `CHECK_VALUE`, `CHECK_STRING`, and `CHECK_NAME` provide assertion helpers. `nbt_test_wins_name()` is the main scenario runner for one name/type/flag combination. It uses `nbt_name_release()`, `nbt_name_register_wins()`, asynchronous `nbt_name_register_send()`/`recv()`, `nbt_name_query()`, `nbt_name_refresh_wins()`, and `nbt_name_release()` to exercise a full lifecycle. `test_nbt_wins_scope_string()` creates long dotted scope strings for boundary tests. `nbt_test_wins()` generates a random base name and runs lifecycle tests across client, master, server, logon, browser, PDC, unusual type bytes, scoped names, empty/dot names, binary-ish names, and long scopes. `nbt_test_wins_bad_names()` verifies names with shell-sensitive characters do not trigger the WINS hook while normal safe names do. `torture_nbt_wins()` registers `wins` and `wins_bad_names`.

## Control Flow
`nbt_test_wins_name()` chooses a local interface IP, tries to bind the client socket to the low NBT port so the server sees the expected source, and falls back to an ephemeral port if needed. It first releases the name, optionally tests wrong-address registration and WACK/resend handling, registers the correct address through WINS, validates the returned WINS server and rcode, then queries the name. For successful names it checks returned addresses, case-sensitive lookup behavior, refreshes TTL, releases the name twice, and verifies final absence except for group-name semantics. `nbt_test_wins()` repeatedly mutates `struct nbt_name` fields and accumulates boolean success. `nbt_test_wins_bad_names()` removes a known hook-output file, runs a WINS lifecycle with each test name, polls for hook output, and asserts hook execution only for allowed names.

## State And Persistence
The test intentionally mutates WINS database state by registering and releasing names. It uses random name suffixes to reduce collisions and explicit release operations to clean up. Wrong-address registration and refresh paths temporarily place alternate records in the WINS database. `wins_bad_names` uses a persistent test file under `SELFTEST_TMPDIR` to observe hook execution and removes it before and after cases.

## Dependencies
Dependencies include NBT name registration/query/refresh/release APIs, async request queues, DLIST queue manipulation, tevent, socket binding, local interface selection, generated NBT constants, `SELFTEST_TMPDIR`, and server-side WINS hook configuration for the hook-specific test. It relies on `torture_nbt_get_name()` to resolve the WINS server address.

## Integration Points
The suite is added by `torture_nbt_init()`. It exercises Samba's WINS server and database behavior from the client side and overlaps with WINS hook shell-safety validation. The asynchronous resend path directly manipulates an NBT request back into the socket send queue after a WACK, so it integrates deeply with the NBT client state machine.

## Risks
This is highly environment-sensitive: inability to bind the low port skips wrong-address conflict checks, missing `SELFTEST_TMPDIR` can break hook observation, and packet loss can cause timeouts. The lifecycle intentionally changes WINS state and may leave records if assertions abort before release. The bad-name test treats some failures as expected DN syntax failures, so diagnosis requires reading comments and output. Long scope and unusual byte-name tests may expose encoding or database-layer assumptions.

## Test Signals
Signals include expected rcodes (`NBT_RCODE_OK`, `NBT_RCODE_ACT`, `NBT_RCODE_SVR`), correct returned WINS server, query address matching either the client IP or broadcast for some group names, object-not-found after release, failure for case-changed name/scope lookups, WACK/resend tolerance, and hook output only for safe names. Failures often point directly to WINS database semantics, source-address handling, or hook sanitization.
