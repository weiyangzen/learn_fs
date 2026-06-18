# sources/test-tools/syzkaller/pkg/asset/type.go

## Purpose
Defines metadata for supported dashboard asset types.

## Important APIs, Types, and Functions
`TypeDescription` describes multiplicity, title function, content type/encoding, reporting priority, reporting suppression, custom compressor, and extension preservation. `assetTypes` maps dashboard asset types to descriptions. `QueryTypeTitle`, `constTitle`, and `GetTypeDescription` expose lookup behavior.

## Control Flow
Lookup is a simple map access. Kernel object title can use target-specific `KernelObject`; other types use constant titles.

## State and Persistence Behavior
Static package-level metadata only.

## Dependencies and Integration Points
Depends on `dashapi.AssetType` and `targets.Target`. Consumed by config validation, upload content metadata, compression choice, and reporting ordering.

## Risks and Test Signals
Unknown asset types return nil and must be checked by callers. HTML coverage uses gzip with preserved extension and no reporting, which is important browser behavior. Covered indirectly by storage/config tests.
