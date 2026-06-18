# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_async.c

Purpose: provides async NLM callback scheduling, callback RPC transport, and acknowledgement signalling for NLM message procedures and granted-lock callbacks.

Important APIs/types/functions: exports `nlm_send_async_res_nlm4`, `nlm_send_async_res_nlm4test`, `find_peer_addr`, `nlm_send_async`, and `nlm_signal_async_resp`. It defines `nlm_reply_proc`, `nlm_async_resp_mutex`, `nlm_async_resp_cond`, and a single `resp_key`.

Control flow: response-scheduling helpers deep-copy cookies into a `state_async_queue_t` and call `state_async_schedule`. `nlm_send_async` lazily creates/reuses callback clients, handles TCP address binding and rpcbind lookup, retries failures, performs a one-shot RPC call, optionally waits up to five seconds for `nlm_signal_async_resp`, and tears down failed callback clients.

State and persistence: maintains per-NLM-client callback RPC client/auth handles and global wait state for one response key. It does not persist data but controls callback completion and blocking-lock grant acknowledgement.

Dependencies and integration points: depends on TI-RPC client APIs, rpcbind, state async queues, NLM XDR routines, `nfs_param`, and network address helpers.

Risks and test signals: global `resp_key` serializes acknowledgement waits and can be sensitive to concurrent callbacks. TCP callback setup, IPv4-mapped IPv6 conversion, retry handling, and copied result ownership are high-risk. Test TCP/UDP callbacks, DNS failures, rpcbind failure, callback timeout, granted acknowledgement signalling, denied TEST holder copy, and async schedule failure cleanup.
