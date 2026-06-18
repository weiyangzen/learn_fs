# sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalc.hh

Purpose: defines the abstract interface for checksum calculation algorithms and plugin calculators.

Important APIs: `Calc()` provides a default one-shot implementation over `Init`, `Update`, and `Final`. `Combinable()` and `Combine()` support algorithms that can combine adjacent block checksums. `Current()` defaults to `Final()`. Pure virtual methods are `Final`, `Init`, `New`, `Type`, and `Update`; `Recycle()` deletes by default. The header documents the external `XrdCksCalcInit()` plugin factory.

Control flow and integration: managers request new calculator instances via `New()` or plugin factory entry points, stream file data through `Update()`, then call `Final()` for binary checksum bytes.

State and persistence: base class stores no state. Concrete calculators own algorithm state and return pointers valid until object deletion or reuse.

Dependencies: none beyond C++ class declarations.

Risks and test signals: algorithm implementations should be tested for repeated `Init()` reuse, one-shot versus incremental equality, `Current()` side effects, correct `Type()` byte sizes, and plugin ABI/version declarations.
