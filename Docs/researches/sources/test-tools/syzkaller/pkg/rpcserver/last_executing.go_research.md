# sources/test-tools/syzkaller/pkg/rpcserver/last_executing.go

## Purpose

`last_executing.go` keeps recent executor programs per proc so crash reports can be prefixed with the programs most likely running at crash time.

## Important APIs, Types, And Control Flow

`LastExecuting` stores a ring of `ExecRecord` values for each proc plus a never-dropped list of hanged programs. `MakeLastExecuting` allocates `procs * count` ring slots. `Note` records the program, proc, ID, and monotonic timestamp in the proc's ring position. `Hanged` appends a record with a synthetic proc ID above `prog.MaxPids` so repro extraction includes it. `Collect` concatenates rings and hanged entries, sorts by start time, drops zero records, converts absolute start times into "duration ago", and invalidates internal slices. `PrependExecuting` writes these records into `report.Report.Output` and adjusts report offsets.

## State, Dependencies, Integration, Risks, And Test Signals

The type is not internally synchronized; callers use it from the runner connection goroutine and shut it down before collecting. It depends on `prog.MaxPids`, monotonic time from callers, and `report.Report` offsets. Risks include panics for invalid proc indexes, use-after-`Collect`, losing older non-hanged entries per proc, and incorrect offset adjustment if the prepended buffer length changes. Tests cover empty collection, ring wrap, ordering, duration conversion, and hanged record retention.
