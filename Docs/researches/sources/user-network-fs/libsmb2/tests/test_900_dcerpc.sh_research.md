<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_900_dcerpc.sh -->
# sources/user-network-fs/libsmb2/tests/test_900_dcerpc.sh

Purpose: Runs the offline DCE/RPC coder regression test.

Important APIs, types, and functions: Invokes `./smb2-dcerpc-coder-test || failure`.

Control flow: Linear shell wrapper around the compiled coder test.

State and persistence behavior: No persistent state.

Dependencies and integration points: Depends on the coder test binary and shared failure helper.

Risks: Only covers fixtures embedded in the C test; does not exercise network DCE/RPC.

Test signals: Direct byte-level DCE/RPC codec regression signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_900_dcerpc.sh -->
