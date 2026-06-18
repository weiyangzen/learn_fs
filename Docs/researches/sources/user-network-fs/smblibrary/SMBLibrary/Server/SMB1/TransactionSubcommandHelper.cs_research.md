# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/TransactionSubcommandHelper.cs

## Purpose

Implements SMB1 Transaction named-pipe subcommands that are supported outside Transaction2.

## Important APIs, Types, And Functions

`GetSubcommandResponse` handles `TRANS_TRANSACT_NMPIPE` by issuing `FSCTL_PIPE_TRANSCEIVE`; `ProcessSubcommand` handles `TRANS_WAIT_NMPIPE` by issuing `FSCTL_PIPE_WAIT`.

## Control Flow

TransactNamedPipe validates FID, sends write data to `DeviceIOControl`, accepts success or buffer overflow, and returns read data. WaitNamedPipe validates `\PIPE\` naming, builds a `PipeWaitRequest`, and calls `DeviceIOControl` without a file handle.

## State And Persistence Behavior

Named-pipe state lives in the file store or pipe service. The helper only reads open-file state for transceive.

## Dependencies And Integration Points

Depends on transaction named-pipe command classes, `PipeWaitRequest`, `IoControlCode`, `SMB1Session`, and `INTFileStore.DeviceIOControl`.

## Risks And Edge Cases

If the wait name does not start with `\PIPE\`, the method sets invalid status but continues to `Substring(6)`, which can throw or use a bad pipe name. Transceive requires a valid FID and does not enforce share-specific access checks here.

## Test Signals

Test named-pipe transceive success, buffer overflow, invalid FID, invalid wait-name short string, wait timeout propagation, and unsupported pipe operations in `TransactionHelper`.

Source-read signal: reviewed the complete local source file for this item.
