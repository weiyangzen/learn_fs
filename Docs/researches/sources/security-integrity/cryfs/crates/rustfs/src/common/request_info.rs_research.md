# sources/security-integrity/cryfs/crates/rustfs/src/common/request_info.rs

Purpose: captures caller identity for a filesystem request.

Important APIs: `RequestInfo { uid: Uid, gid: Gid, pid: u32 }`.

Control flow and state: copyable data passed through all high-level and low-level trait methods.

Dependencies and integration: initialized by backend adapters from FUSE request metadata and used by object adapters when creating nodes with caller ownership. Test helper `assert_request_info_is_correct` verifies propagation in mkdir tests.

Risks and tests: only uid/gid/pid are represented; groups, capabilities, and security labels are out of scope.
