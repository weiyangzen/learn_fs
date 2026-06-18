# sources/test-tools/syzkaller/pkg/subsystem/linux/names.go

## Purpose

`names.go` assigns stable short names to generated Linux subsystems. Names are needed for bug labels, email subjects, service lookup, custom rule binding, and parent debug output.

## Important APIs, Types, and Functions

`setSubsystemNames` validates pre-existing names and fills empty names from the first mailing-list address. `validateName` constrains generated names to 2 through 16 characters. `emailToName` applies explicit `emailExceptions`, then `emailStripRe`. `buildEmailStripRe` composes prefix and suffix stripping rules from `stripPrefixes` and `stripSuffixes`.

## Control Flow

The first pass over the list rejects duplicate explicit names and records them in a map. The second pass skips already named subsystems, requires at least one list address, derives a name from the first list, validates length, rejects collisions with existing or generated names, then mutates `item.Name`. `emailToName` first checks hard-coded exceptions for renamed or overly long lists, then strips repeated prefixes like `linux-` and suffixes like `-devel`, `-dev`, `-list`, and related terms before `@`.

## State, Dependencies, Risks, and Test Signals

The function mutates the supplied subsystem list in place and persists no external data. Dependencies are `fmt`, `regexp`, `strings`, and `subsystem.Subsystem`. Integration points include `listFromRepoInner` and `applyExtraRules`, which assume all names are unique. Risks include first-list dependence, incomplete exception coverage, length constraints rejecting legitimate subsystems, and regex changes causing label churn. `names_test.go` covers general stripping, exceptions, collisions, explicit names, and missing-list failure.
