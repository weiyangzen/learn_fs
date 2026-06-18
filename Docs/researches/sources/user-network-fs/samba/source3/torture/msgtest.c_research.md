# sources/user-network-fs/samba/source3/torture/msgtest.c

## Purpose
`msgtest.c` is an older standalone internal messaging test and speed probe. It sends `MSG_PING` messages to another process and to itself, counts `MSG_PONG` replies, and reports throughput.

## Important APIs, types, and functions
The important callback is `pong_message`, registered for `MSG_PONG`, which increments global `pong_count`. `main()` initializes locale, logging, loadparm, tevent, and messaging; parses `<pid> <count>`; registers the callback; sends messages via `messaging_send` and `messaging_send_buf`; and drives `tevent_loop_once`.

## Control flow
The first phase sends `n` pings to the given PID and loops until `pong_count` reaches the sent count. The second phase sends both empty and buffered pings to itself and loops until two replies per iteration arrive. The final speed phase sends paired buffered/unbuffered pings for `n` seconds while keeping outstanding pings bounded, then waits up to 30 seconds for replies.

## State and persistence behavior
State is limited to `pong_count`, local tevent/messaging contexts, and transient message queues. No durable data is written.

## Dependencies and integration points
It exercises Samba's process messaging APIs and expects a peer that replies to `MSG_PING` with `MSG_PONG`, normally an smbd/nmbd-style Samba process. It uses `pid_to_procid` and `messaging_server_id` for addressing.

## Risks and test signals
The test can hang or undercount if the peer is not running, not responding to ping, or the event loop stops. Failure messages distinguish local self-delivery count failures from remote ping loss. Throughput output is approximate and environment-dependent.
