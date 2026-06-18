# sources/test-tools/stress-ng/core-time.h

## Purpose
`core-time.h` declares the common time conversion, current-time, and duration-formatting helpers.

## Important APIs, Types, And Functions
Exports are `stress_time_timeval_to_double`, `stress_time_now`, and `stress_time_duration_to_str`. Attributes mark conversion as `CONST` and duration formatting as non-null returning.

## Control Flow
Callers use `stress_time_now` for loop deadlines and metric deltas, and `stress_time_duration_to_str` for display strings. The header does not define runtime logic.

## State And Persistence
No state is defined here. Implementation state includes a static fallback function pointer and static formatting buffer.

## Dependencies And Integration Points
It includes `core-attribute.h` and relies on `struct timeval`, `bool`, and common type visibility from the include environment. Nearly every stressor can indirectly depend on this API for timing and metrics.

## Risks
The static-buffer return contract is not visible in the prototype, so callers must not store the returned pointer across later formatting calls. Include ordering must provide system time and boolean types.

## Test Signals
Build coverage across platforms and runtime metric/status output validate the API. Any change that alters return precision or buffer lifetime can affect many stressors.
