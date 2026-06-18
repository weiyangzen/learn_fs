# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/TransactionHelper.cs

## Purpose

Assembles, dispatches, and fragments SMB1 Transaction and Transaction2 requests and responses.

## Important APIs, Types, And Functions

`GetTransactionResponse` overloads handle primary and secondary transaction packets. `GetCompleteTransactionResponse` dispatches named-pipe transaction subcommands. `GetCompleteTransaction2Response` dispatches Transaction2 subcommands. The final overload fragments response setup/parameters/data into one or more response commands.

## Control Flow

Primary packets with incomplete parameter/data payloads allocate process state and return interim. Secondary packets copy fragments by displacement and return no command until complete. Complete transactions parse subcommands, set header status, build subcommand response data, and fragment when calculated response size exceeds `MaxBufferSize`.

## State And Persistence Behavior

Uses connection process-state assembly and open-search/file-store state through subcommand helpers. Named-pipe and filesystem operations are delegated.

## Dependencies And Integration Points

Depends on SMB1 transaction classes, `ProcessStateObject`, `TransactionSubcommandHelper`, `Transaction2SubcommandHelper`, and `INTFileStore` via shares.

## Risks And Edge Cases

Fragment assembly keyed only by PID is fragile for concurrent transactions. Duplicate/overlapping fragments can overcount received bytes. Response fragmentation primarily splits data, with parameters sent in the first response only. RAP/LANMAN requests are explicitly not implemented.

## Test Signals

Test primary-only and multi-secondary assembly, invalid parse status, unsupported subcommands, transaction2 dispatch, max-buffer fragmentation, zero-length parameters/data, and PID collision behavior.

Source-read signal: reviewed the complete local source file for this item.
