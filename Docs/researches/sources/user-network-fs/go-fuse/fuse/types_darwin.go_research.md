# `sources/user-network-fs/go-fuse/fuse/types_darwin.go`

## Purpose
Darwin protocol type and capability definitions.

## Important APIs, Types, And Functions
Defines Darwin `Attr`, Darwin `SetAttrIn`, xattr request shapes, macFUSE capabilities, `GetxtimesOut`, `ExchangeIn`, `MonitorIn`, errno aliases, and Darwin `StatfsOut.FromStatfsT`/`InitOut.setFlags`.

## Control Flow
Defines Darwin `Attr`, Darwin `SetAttrIn`, xattr request shapes, macFUSE capabilities, `GetxtimesOut`, `ExchangeIn`, `MonitorIn`, errno aliases, and Darwin `StatfsOut.FromStatfsT`/`InitOut.setFlags`.

## State And Persistence
State is wire layout only. Risks are macFUSE ABI/capability bit differences and block-size adjustment in statfs conversion. Integrated by all Darwin builds.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is wire layout only. Risks are macFUSE ABI/capability bit differences and block-size adjustment in statfs conversion. Integrated by all Darwin builds.

## Test Signals
State is wire layout only. Risks are macFUSE ABI/capability bit differences and block-size adjustment in statfs conversion. Integrated by all Darwin builds.
