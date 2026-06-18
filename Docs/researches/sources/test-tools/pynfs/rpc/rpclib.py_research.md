# sources/test-tools/pynfs/rpc/rpclib.py

Purpose: small RPC flow-control and reply-building helper library used by the transport when request processing should stop and a specific RPC reply should be emitted.

Important APIs/types/functions: `NULL_CRED`, `RPCFlowContol`, `RPCDrop`, `RPCDeniedReply`, `RPCUnsuccessfulReply`, and `RPCSuccessfulReply`.

Control flow: server-side RPC handling raises these exceptions to short-circuit normal procedure processing. Each reply exception has a `body()` method that builds an accepted or denied `reply_body` plus optional payload bytes. `RPCDrop` signals silent drop.

State and persistence behavior: no persistent state. Instances store status codes, mismatch/auth data, verifier, or message data for one reply.

Dependencies/integration: used by `rpc.py` and `security.py`; imports generated RPC constants/types and builds `rejected_reply`, `accepted_reply`, `rpc_reply_data`, and `rpc_mismatch_info` objects.

Risks and test signals: class name `RPCFlowContol` is misspelled but consistently used. Broad exception handling inside `body()` masks construction bugs by returning generic auth/system errors while logging critical messages.
