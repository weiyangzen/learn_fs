## sources/user-network-fs/go-fuse/fuse/opcode_darwin.go

Purpose: Darwin-specific registration for macFUSE monitor opcode.

Important APIs/types/functions: `_OP_MONITOR`, `doMonitor`, and init-time `operationHandlers[_OP_MONITOR]` entry with `MonitorIn` input.

Control flow: monitor notifications suppress replies and do not call filesystem handlers.

State and persistence: mutates global opcode handler table at init.

Dependencies and integration: extends `opcode.go` for macFUSE-specific advisory events.

Risks and test signals: missing registration can break macFUSE notifications. `opcode_darwin_test.go` verifies the handler exists.
