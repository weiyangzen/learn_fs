
# sources/user-network-fs/samba/source4/torture/nbt/register.c

## Purpose
`register.c` defines NBT name registration and refresh tests that verify a server defends its own NetBIOS name. It attempts to register and refresh the target server's name from the local client and expects the server to answer with an active-name conflict response.

## Important APIs, Types, And Functions
Macros `CHECK_VALUE` and `CHECK_STRING` wrap torture assertions for integer and case-insensitive string comparisons. `nbt_register_own()` builds a `struct nbt_name_register` request for the resolved server name, binds a local NBT socket, sends normal registration and register-demand variants, and checks `NBT_RCODE_ACT`. `nbt_refresh_own()` sends `struct nbt_name_refresh` for the server's name and also expects `NBT_RCODE_ACT`. `torture_nbt_register()` creates the `register` suite and adds `register_own` and `refresh_own`.

## Control Flow
Both tests resolve the target name/address with `torture_nbt_get_name()`, choose the best local interface address for reaching the target, bind a socket on an ephemeral local port, populate request fields with target name, target NBT port, local address, B-node active flags, TTL, timeout, and retry count, then call the synchronous NBT client API. Assertions validate that the response name/type matches the target and that the response code indicates active conflict.

## State And Persistence
The tests do not intend to create persistent server state; they attempt operations that should be rejected/defended by the target owner. Local socket state is transient. If a server incorrectly accepts the registration, it may mutate name-service state, which is exactly the failure this test is meant to catch.

## Dependencies
Dependencies include NBT socket APIs, Samba socket abstraction, resolver helpers, interface selection, loadparm NBT port, and torture assertion macros. The environment must support local UDP sockets and a target server reachable by NetBIOS name service.

## Integration Points
The suite is registered from `nbt.c`. It shares helper functions with the WINS and benchmark tests and validates the same target resolved from the `host` setting. These tests are low-level signals for name ownership behavior that WINS and datagram tests depend on indirectly.

## Risks
The tests assume the best local interface IP chosen for the target is acceptable to the server. Firewalls, disabled NetBIOS service, or NAT can produce failures unrelated to server name defense. The refresh test comment contains a typo in an assertion message, but behavior is unaffected. Because retries are zero and timeout is three seconds, transient packet loss can fail the test.

## Test Signals
Positive signals are NTSTATUS success from `nbt_name_register()`/`nbt_name_refresh()`, echoed name/type values, and `NBT_RCODE_ACT`. Any `NBT_RCODE_OK` for the server's own name is a serious behavioral failure. Socket bind or resolution failures identify environment problems before protocol assertions run.
