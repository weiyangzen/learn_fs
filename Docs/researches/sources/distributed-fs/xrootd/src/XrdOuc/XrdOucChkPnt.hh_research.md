# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucChkPnt.hh

## Purpose
Defines an abstract checkpoint interface for file implementations that support create, restore, truncate, write, and cleanup of checkpointed file state.

## Important APIs, Types, And Functions
`XrdOucChkPnt` declares pure virtual methods `Create`, `Delete`, `Finished`, `Query(iov&)`, `Restore(bool*)`, `Truncate(iov*&)`, and `Write(iov*&, int)`. The interface uses `struct iov` from `XrdOucIOVec.hh` by forward declaration for offset/length/vector data.

## Control Flow
Consumers obtain an implementation object, call `Create`, stream writes/truncates through `Write` and `Truncate`, query limits with `Query`, restore with `Restore`, and end lifecycle with `Finished`. The destructor comment says use `Finished()` rather than deleting directly, allowing implementations to self-delete or clean outstanding checkpoint files.

## State And Persistence
The interface itself has no state, but implementations are expected to manage persistent checkpoint data and restore/truncate semantics. `Restore` can report whether read access remains safe after an error through `readok`.

## Dependencies And Integration Points
It is an integration contract between storage/cache code and checkpoint backends. It depends on `iov` layout compatibility and errno-style return values.

## Risks And Test Signals
Risks include ambiguous ownership of `iov*&` ranges, callers deleting instead of calling `Finished`, and inconsistent restore behavior after partial checkpoint failures. Test signals include create/delete idempotence, write/truncate ordering, restore after failure, checkpoint length queries, and implementations returning `-errno` consistently.
