# sources/test-tools/strace/tests/netlink_crypto.c

Purpose: tests `NETLINK_CRYPTO` decoding for crypto netlink message types, flags, and `struct crypto_user_alg` payloads.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_CRYPTO)`, `sendto`, `struct nlmsghdr`, `CRYPTO_MSG_*`, `struct crypto_user_alg`, `TEST_NETLINK_OBJECT_EX`, `TEST_NETLINK_`, `midtail_alloc`, `fill_memory_ex`, `PRINT_FIELD_X`, and `PRINT_FIELD_U`.

Control flow: `main` creates a crypto netlink socket, checks type decoding with `CRYPTO_MSG_NEWALG`, checks flag decoding for get/new/del/update operations, sends structured `crypto_user_alg` payloads with short and long string fields, and finally sends an unknown message type with raw bytes.

State and persistence: no persistent crypto state is intended. All messages are test buffers sent nonblocking; fd and memory buffers are transient.

Dependencies and integration points: uses Linux `cryptouser.h`, strace netlink test macros, and the `netlink_protocols` xlat macros for symbolic protocol names.

Risks and edge cases: string truncation with fixed-size `cru_*` arrays, unknown flag combinations, and unknown message types are deliberate edge cases. Header availability can affect constants.

Test signals: output must show symbolic crypto message names, correct flag rendering or `NLM_F_???` fallback, structured `crypto_user_alg` fields, raw unknown payload, and normal exit.
