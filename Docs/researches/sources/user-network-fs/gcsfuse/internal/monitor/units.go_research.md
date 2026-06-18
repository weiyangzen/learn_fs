## sources/user-network-fs/gcsfuse/internal/monitor/units.go

### Purpose
`units.go` centralizes metric unit constants used by monitoring code.

### Important APIs, Types, And Functions
It exports `UnitDimensionless`, `UnitMicroseconds`, and `UnitBytes`. Dimensionless and bytes reuse OpenCensus unit constants; microseconds is a literal `"us"`.

### Control Flow
There is no runtime control flow.

### State, Persistence, And Dependencies
There is no state. The only dependency is `go.opencensus.io/stats`.

### Integration Points
Metric definitions can import these constants to avoid unit string drift across monitoring packages.

### Risks
The file mixes OpenCensus unit constants with OTel metric infrastructure elsewhere; migrations should preserve unit names consumed by dashboards.

### Test Signals
No tests are necessary beyond compile-time usage, though dashboard compatibility is the practical signal.
