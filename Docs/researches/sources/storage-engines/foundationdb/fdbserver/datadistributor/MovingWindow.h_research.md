# sources/storage-engines/foundationdb/fdbserver/datadistributor/MovingWindow.h

Purpose: defines a small template utility for uniformly weighted moving-window averages over recent samples. It is intended for DD telemetry such as recent bytes-moved rates, where an exact windowed average is preferable to exponential smoothing.

Important APIs and types: `template<class T> class MovingWindow` exposes `MovingWindow(double timeWindow)`, `addSample(T)`, `getAverage()`, and `getTotal()`. Internal fields are `previous`, `total`, `maxDequeSize`, `Deque<std::pair<double,T>> updates`, `interval`, and `previousPopTime`.

Control flow: `addSample()` increments the lifetime total, appends `(now(), sample)`, and evicts oldest entries if the deque exceeds a knob-derived memory cap. `getAverage()` either divides samples accumulated since initialization or forced eviction by elapsed time, or evicts entries older than `now() - interval` and divides the active sum by the fixed interval. Eviction moves values into `previous`, leaving `total - previous` as active-window mass.

State and persistence: state is in-memory only. `total` is monotonic over object lifetime, while `previous` tracks samples outside the active window or evicted by memory pressure. `previousPopTime` is used to avoid dividing by the full interval before the window has aged in or after forced eviction.

Dependencies and integration: uses Flow `Deque`, `now()`, and `SERVER_KNOBS->MOVING_WINDOW_SAMPLE_SIZE`. It is a header-only utility and can be embedded in DD actors without a separate implementation file.

Risks: `getAverage()` may divide by a very small elapsed time immediately after construction or eviction. `maxDequeSize` depends on `sizeof(std::pair<double,T>)`; very large `T` or an unexpectedly low knob can force frequent eviction and reduce window fidelity. It assumes `T` supports zero construction, addition, subtraction, and division-compatible conversion to `double`.

Test signals: no local unit tests in this header. Useful tests would cover cold-start averaging, expiration, max-deque eviction, zero/near-zero elapsed time behavior, and non-integer sample types.
