# sources/user-network-fs/mergerfs/src/policy_msplus.hpp

## Purpose
Declares the `Policy::MSPLUS` policy family for mergerfs operation routing. The policy name is `msplus`, representing the most-shared-path least-used-space selection strategy exposed through the common policy registry.

## Important APIs, Types, and Functions
The header defines final `Action`, `Create`, and `Search` classes derived from `Policy::ActionImpl`, `Policy::CreateImpl`, and `Policy::SearchImpl`. Each class overrides `operator()(const Branches::Ptr&, const fs::path&, std::vector<Branch*>&)`. `Create::path_preserving()` returns `false`, so create placement may choose a branch independent of an already existing full target path.

## Control Flow
Construction only passes the policy string to the base class. Runtime control flow is implemented in the matching `.cpp` file or, for `policy_lup.hpp`, an implementation elsewhere; callers dispatch through the polymorphic policy interface and receive selected `Branch*` entries in the output vector.

## State and Persistence Behavior
The declarations carry no mutable state. Persistence is indirect: selected branches determine where later filesystem operations create, modify, or search backing files.

## Dependencies and Integration Points
It depends on `policy.hpp`, `Branches`, `Branch`, and the mergerfs policy registration layer. FUSE operation handlers consume these policy objects through category-specific create/action/search configuration.

## Risks and Edge Cases
Header and implementation names must stay synchronized with `policies.hpp` and config parsing. Since the classes are final, behavior extension requires adding a new policy rather than subclassing these declarations.

## Test Signals
Policy tests should confirm the configured policy name maps to these classes, create/search/action calls return expected branches, and `path_preserving()` behavior is reflected in path creation cases.
