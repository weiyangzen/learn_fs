# sources/storage-engines/foundationdb/fdbserver/worker/RoleLineage.cpp

## Purpose
`RoleLineage.cpp` provides the out-of-class definition for the static lineage property name used by `RoleLineage`.

## Important APIs, Types, And Functions
It defines `std::string_view RoleLineage::name = "RoleLineage"sv;`, enabling `LineageProperties<RoleLineage>` to identify the property set by name.

## Control Flow
There is no runtime control flow beyond static initialization.

## State And Persistence Behavior
The only state is a static string view; there is no persistence.

## Dependencies And Integration Points
It includes `RoleLineage.h` and uses `std::literals`. The definition is required by any translation unit that uses the `RoleLineage::name` static member.

## Risks And Test Signals
Risk is low. Missing this definition would produce link errors for lineage profiling users.
