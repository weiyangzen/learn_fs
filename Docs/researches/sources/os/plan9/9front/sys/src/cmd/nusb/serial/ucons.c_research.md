# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/serial/ucons.c

## Role

Provides a minimal USB console-style serial probe shim.

## Main Behavior

The file matches two device families: Ajays Net20DC USB debug cable and Huawei E220. The matched `cid` value is used as `ser->nifcs`, so the probe can expose one or more interfaces.

`uconsprobe` checks VID/PID with `matchid`, sets the interface count, installs `uconsops`, and otherwise leaves behavior to the generic serial framework.

## Integration Points

`uconsops` only provides `.findeps = findendpoints`, relying on generic endpoint handling and default read/write paths.
