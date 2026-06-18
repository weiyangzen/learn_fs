# sources/user-network-fs/go-fuse/example/winfs/main.go

Purpose: loopback filesystem variant that emulates Windows semantics by rejecting unlink/rename of open files.

Important types/functions: `WindowsNode` embeds `fs.LoopbackNode` and tracks `openCount` under a mutex. `Open` and `Create` increment counts; `Release` decrements and forwards file release; `isBusy` sleeps for a configurable delay then checks child open count; `Unlink` and `Rename` return `EBUSY` when source or destination is busy. `newWindowsNode` customizes `LoopbackRoot.NewNode`.

State/dependencies: persistent state lives in the backing filesystem; transient open counts live in each node.

Risks/integration: the delay is a race workaround because kernel close does not synchronize release before subsequent operations. It depends on deprecated `LoopbackRoot.NewNode`. Test signal is manual behavior and analogous Windows example tests elsewhere.
