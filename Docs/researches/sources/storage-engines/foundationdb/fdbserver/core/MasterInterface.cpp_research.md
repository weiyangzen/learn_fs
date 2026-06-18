# sources/storage-engines/foundationdb/fdbserver/core/MasterInterface.cpp

## Purpose
Provides explicit template instantiations for `MasterInterface` RPC serialization support.

## Important APIs, Types, and Functions
- `template class ReplyPromise<MasterInterface>;`
- `template struct NetSAV<MasterInterface>;`

## Control Flow
No runtime control flow beyond compilation/linkage of template instantiations.

## State and Persistence Behavior
No state or persistence behavior.

## Dependencies and Integration Points
Includes `fdbserver/core/MasterInterface.h`. The explicit instantiations ensure the master interface can be used in reply promises and network serialization/address vector contexts without relying solely on implicit instantiation in downstream translation units.

## Risks and Edge Cases
The file is intentionally tiny; removing it can surface link errors rather than local compile errors. Any change to `MasterInterface` serialization requirements may need corresponding instantiations here or in related files.

## Test Signals
The primary signal is successful linkage of fdbserver core and components that use `MasterInterface` RPCs.
