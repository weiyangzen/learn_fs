# sources/storage-engines/tikv/components/raftstore/src/store/cmd_resp.rs

Purpose: Centralizes small helpers for building raft command responses with current term and structured raftstore errors.

Important APIs and types: `bind_term` writes `current_term` into a `RaftCmdResponse` header when term is nonzero. `bind_error` converts crate `Error` into `errorpb::Error` and stores it in the response header. `new_error` constructs an error response. `err_resp` combines error and term binding. `message_error` boxes a generic error into `Error::Other` and returns a response.

Control flow: Helpers mutate or construct protobuf responses directly. `bind_term` is a no-op for zero, preserving responses where no current term is known. Error conversion delegates to `errors.rs`, so structured fields depend on the `Error` variant.

State and persistence: No durable state. These helpers shape client-visible command results after raftstore processing failures or leadership/term changes.

Dependencies and integration points: It depends on `kvproto::raft_cmdpb::RaftCmdResponse` and crate `Error`. Store command handling code can use these helpers to produce consistent error responses without duplicating header manipulation.

Risks: `message_error` wraps errors as `Error::Other`, which produces mostly message-only client errors and unknown error codes. Callers must pass a nonzero term when term redirection semantics matter.

Test signals: No local tests. Behavior is indirectly tested by `errors.rs` conversion tests and raftstore command handling tests.
