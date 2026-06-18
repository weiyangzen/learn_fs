# `sources/user-network-fs/go-fuse/internal/ioctl/ioctl.go`

## Purpose
Utility package for constructing and inspecting Linux ioctl command numbers.

## Important APIs, Types, And Functions
Defines direction constants, `Command`, `New`, and accessors such as read/write/type/number/size decoding.

## Control Flow
Defines direction constants, `Command`, `New`, and accessors such as read/write/type/number/size decoding.

## State And Persistence
No persistence. Integrated by ioctl tests and FUSE IOCTL handlers. Risk is command bitfield layout and panic on sizes >=16 KiB.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persistence. Integrated by ioctl tests and FUSE IOCTL handlers. Risk is command bitfield layout and panic on sizes >=16 KiB.

## Test Signals
No persistence. Integrated by ioctl tests and FUSE IOCTL handlers. Risk is command bitfield layout and panic on sizes >=16 KiB.
