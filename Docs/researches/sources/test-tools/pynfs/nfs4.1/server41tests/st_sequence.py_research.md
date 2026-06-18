# sources/test-tools/pynfs/nfs4.1/server41tests/st_sequence.py

Purpose: NFSv4.1 `SEQUENCE` protocol tests for operation position, session binding, bad sessions/slots, request and operation limits, replay cache behavior, op-not-in-session errors, returned sequence fields, and sequence misordering.

Important APIs/types/functions: `testSupported`, `testNotFirst`, `testImplicitBind`, `testBadSession`, `testRequestTooBig`, `testTooManyOps`, `testBadSlot`, replay-cache tests `testReplayCache001` through `testReplayCache007`, `testOpNotInSession`, `testSessionidSequenceidSlotid`, and `testBadSequenceidAtSlot`.

Control flow: tests create sessions with default or constrained channel attributes, send compounds using session helpers or raw `env.c1.compound`, and use `seq_delta=0` to replay the same slot sequence. Replay tests normalize tags and compare full response structures with `nfs4lib.test_equal`.

State and persistence behavior: focuses on per-session forechannel state: slot ids, sequence ids, cached replies, connection binding, and channel limits. Some replay tests create/rename files to exercise non-idempotent cached replies.

Dependencies/integration: uses `channel_attrs4`, `bad_sessionid`, file helpers, raw NFS client connections, and `nfs4lib.dec_u32`/`test_equal`.

Risks and test signals: `testRequestTooBig` comments that `NAME_TOO_BIG` may be valid but is not accepted by this test. Replay tests depend on exact response equality except tag clearing. Raw slot ids in `testSessionidSequenceidSlotid` may interact with slot-range negotiation.
