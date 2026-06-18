## sources/user-network-fs/go-fuse/fuse/opcode_darwin_test.go

Purpose: unit test for Darwin monitor opcode registration.

Important APIs/types/functions: `TestMonitorOpcodeRegistered` calls `getHandler(_OP_MONITOR)` and checks name and function.

Control flow: simple registration assertion during Darwin test builds.

State and persistence: reads global handler table.

Dependencies and integration: validates `opcode_darwin.go` init side effect.

Risks and test signals: catches accidental removal or overwrite of the macFUSE monitor handler.
