<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/oslockluster.go -->
# sources/security-integrity/libcap/cap/oslockluster.go

## Purpose
Pre-Go-1.10 launch support stub. It disables `Launcher` functionality when the Go runtime cannot safely terminate locked OS threads on return.

## Important APIs, Types, And Functions
Defines `LaunchSupported = false` and `validatePA` returning `ErrNoLaunch`.

## Control Flow
Build-tag selection causes `Launch` to fail early on unsupported toolchains.

## State And Persistence Behavior
No state is changed because launch is rejected.

## Dependencies And Integration Points
Selected by build tag `!go1.10`; used by `launch.go`.

## Risks And Edge Cases
Applications using launch must handle `ErrNoLaunch` or require newer Go.

## Test Signals
Signals are `LaunchSupported` false and expected `ErrNoLaunch`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/oslockluster.go -->
