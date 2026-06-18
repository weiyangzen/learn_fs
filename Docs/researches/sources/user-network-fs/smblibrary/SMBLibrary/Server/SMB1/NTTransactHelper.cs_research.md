# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/NTTransactHelper.cs

## Purpose

Assembles and dispatches SMB1 NT transaction requests, including IOCTL, security descriptor set/query, and notify-change.

## Important APIs, Types, And Functions

`GetNTTransactResponse` overloads handle primary and secondary fragments. `GetCompleteNTTransactResponse` dispatches subcommands. Private helpers implement IOCTL, set security descriptor, query security descriptor, and response fragmentation.

## Control Flow

Incomplete requests allocate `ProcessStateObject` and return `NTTransactInterimResponse`. Secondary fragments copy bytes by displacement until complete. Complete requests parse the subcommand, call the relevant helper, return no immediate response for pending notify, or fragment response data against `MaxBufferSize`.

## State And Persistence Behavior

Uses connection process-state assembly and async notify state. Security setters mutate file-store security descriptors; IOCTL and query paths delegate to file-store state.

## Dependencies And Integration Points

Depends on SMB1 NT transaction classes, `NotifyChangeHelper`, `SecurityDescriptor`, `IoControlCode`, `SMB1ConnectionState`, and `INTFileStore` methods.

## Risks And Edge Cases

Assembly is PID-keyed and has overlap-counting issues inherited from `ProcessStateObject`. Response fragmentation loop uses `TransactionResponse.CalculateMessageSize` for additional NT transact responses. Security query returns `STATUS_BUFFER_TOO_SMALL` rather than a partial descriptor.

## Test Signals

Test multi-packet assembly, unknown function status, FSCTL-only rejection, invalid FID, IOCTL buffer overflow, security descriptor set/query, notify pending/completion, and fragmented responses.

Source-read signal: reviewed the complete local source file for this item.
