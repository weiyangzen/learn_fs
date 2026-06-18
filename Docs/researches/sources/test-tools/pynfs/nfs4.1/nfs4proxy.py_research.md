# sources/test-tools/pynfs/nfs4.1/nfs4proxy.py

## Purpose
`nfs4proxy.py` implements an NFSv4 proxy used for testing traffic forwarding, callback forwarding, channel-attribute rewriting, and fault injection. It listens as an RPC server, forwards client COMPOUND and NULL calls to a destination server, can proxy callback traffic over the client's connection, and can inject XML-described errors before forwarding.

## Important APIs, Types, And Functions
- `NFS4Proxy(rpc.Server)` is the proxy server.
- Inner `Channel` stores request/response/cache/ops/requests channel caps used to clamp `CREATE_SESSION` attrs.
- Inner `ProxyClient(rpc.Client)` maintains the downstream or callback connection and sends raw forwarded calls.
- `start`, `start_cb_proxy`, `forward_call`, `handle_0`, `handle_1`, `handle_cb_0`, and `handle_cb_1` are the RPC entry points.
- `op_create_session(arg, cred, direction=0)` rewrites fore/back channel attributes and initializes callback proxying.
- `scan_options()` parses command-line destination/listen options.

## Control Flow
Construction binds the proxy RPC server, creates a `ProxyClient` connected to the destination NFS server, assigns the reverse reference, and loads an `ErrorParser`. For NULL calls, the proxy forwards an empty NULL request to either downstream or callback side and returns success if it receives a response.

COMPOUND handling unpacks request XDR into normal or callback args, creates `CompoundState`/`CBCompoundState`, scans operations, invokes matching proxy override methods, consults `errorhandler.get_error`, and if an injected status is returned, immediately packs a one-operation error reply and returns without forwarding. If no injected error stops the request, it repacks possibly mutated args, forwards raw XDR to the selected client, unpacks the downstream response, runs post-processing override hooks, repacks, and returns to the original caller.

`CREATE_SESSION` pre-processing starts a callback proxy using the client's connection and clamps requested fore/back channel attrs to the proxy's smaller configured channel caps. Callback calls use `handle_cb_*` and `cb_client` to forward traffic back to the original client.

## State And Persistence Behavior
Proxy state is in process memory: downstream client pipe, optional callback client, callback program/version, error parser, channel limits, tag, and RPC server state. It persists no traffic. Error injection can mutate in-flight request objects before forwarding; those mutations only live for that request.

## Dependencies And Integration Points
The module depends on `rpc.rpc`, generated NFSv4 constants/types, SCTRL packers, `nfs4lib`, `nfs4commoncode`, `nfs4client`, `locking`, `errorparser`, logging, traceback, random/hmac/struct/time, and command-line `optparse`. It sits between client tests and an NFSv4 server, including callback traffic.

## Risks And Edge Cases
- Callback request unpacking uses `unpack_CB_COMPOUNDargs`, while other code uses `unpack_CB_COMPOUND4args`; this naming mismatch can break callback proxying.
- Identity checks use `is 0` and `is 1` for integers.
- `ErrorParser(None)` may fail before proxy startup if no error file is supplied.
- Override function results are assigned but mostly ignored unless error injection returns a code.
- `_adjust_channel_values` misspells `ca_maxresponsesize_cached` as `ca_maxresposnesize_cached` in one assignment.
- The proxy supports only one downstream connection and one callback client at a time.
- `forward_call` catches timeouts but not decode/pack errors or connection resets beyond retry loop.
- The injected error reply uses the current operation name and current result accumulator; multi-op prefix behavior is minimal.

## Test Signals
Signals include transparent forwarding of NULL and COMPOUND calls, `CREATE_SESSION` channel clamping, callback proxy setup and callback forwarding, XML error injection returning encoded NFS errors without forwarding, function-based argument mutation, downstream timeout handling, and response repacking preserving server results.
