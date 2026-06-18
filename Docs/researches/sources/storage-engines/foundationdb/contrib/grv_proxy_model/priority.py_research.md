# sources/storage-engines/foundationdb/contrib/grv_proxy_model/priority.py

## Purpose
`priority.py` defines the priority ordering used by the GRV proxy simulator. It gives system, default, and batch traffic comparable objects with stable labels.

## Important APIs, Types, And Functions
`Priority(priority_value, label)` stores a numeric ordering and display label. `functools.total_ordering` derives the remaining comparisons from `__lt__`; `__str__` returns the label and `__repr__` returns the quoted label. Module constants `Priority.SYSTEM`, `Priority.DEFAULT`, and `Priority.BATCH` are assigned values 0, 1, and 2.

## Control Flow
There is no runtime control flow beyond object construction. Priority objects are consumed as dictionary keys and compared in queue processing and budget calculations.

## State And Persistence Behavior
The file creates three singleton-like class attributes. These objects are mutable by convention but not mutated by the simulator after initialization. Nothing is persisted.

## Dependencies And Integration Points
It depends only on `functools`. `workload_model.Request.__lt__`, `proxy_model.ProxyModel.process_requests`, and predefined workload/ratekeeper maps rely on this ordering to process lower numeric priorities first and to sum traffic at or above a priority threshold.

## Risks And Edge Cases
`__eq__` is not explicitly implemented even though `total_ordering` normally expects it; object identity equality is therefore retained. This is acceptable while singleton constants are reused everywhere, but separately constructed `Priority(1, "Default")` objects would compare with `<` but not compare equal. The class has no hash override, so identity hashing matches identity equality.

## Test Signals
Tests should assert `SYSTEM < DEFAULT < BATCH`, string labels, repr labels, and dictionary-key behavior with the predefined singleton objects. A regression would show up as changed request-queue ordering or limiter budget attribution.
