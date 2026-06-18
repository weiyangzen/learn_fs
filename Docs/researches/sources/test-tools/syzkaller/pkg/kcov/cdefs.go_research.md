## sources/test-tools/syzkaller/pkg/kcov/cdefs.go

Purpose: defines Linux KCOV ioctl constants without cgo.

Important APIs/types/functions: build tag `linux`, `sizeofUintPtr`, ioctl bit/shift constants, `kcovInitTrace`, `kcovEnable`, `kcovDisable`, and trace mode constants.

Control flow: no runtime control flow; constants are computed from Linux `_IO*` encoding.

State and persistence: none.

Dependencies and integration: used by `kcov.go` for ioctl calls.

Risks: architecture/ioctl encoding drift would break tracing. Constants assume Linux KCOV ABI.

Test signals: no direct tests; failures surface when enabling KCOV.
