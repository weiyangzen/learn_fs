# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/XrdCephReadVBasic.cc

Purpose: implements a basic readv extent combiner that groups small reads into larger contiguous Ceph reads.

Important APIs/types/functions: destructor logs aggregate used/wasted bytes; `convert` transforms one `ExtentHolder` into a vector of grouped `ExtentHolder` reads.

Control flow: `convert` obtains input extents, sets left/right iterators, shortcuts to one combined holder if total range is below `m_minSize`, otherwise groups consecutive extents until the aggregate range would exceed `m_maxSize`, recording useful and wasted bytes. Stats accumulate across calls.

State and persistence: keeps only aggregate used/wasted byte counters. No persistent state.

Dependencies and integration points: uses `Extent`, `ExtentHolder`, and `BUFLOG`; used by XrdCeph readv file code to reduce many small reads.

Risks: it dereferences `it_end->end()` even though `it_end` equals `extentsIn.end()`, an invalid iterator. The shortcut copy relies on `ExtentHolder(const ExtentContainer&)`, which currently copies from the wrong container. Input is not sorted here, so grouping quality depends on caller ordering. The destructor percentage formula divides by `totalBytes*100` instead of multiplying by 100.

Test signals: empty input, one extent, total below min size, grouping above max size, unsorted extents, iterator sanitizer tests, and stats accounting.
