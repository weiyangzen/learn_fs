# File Research: sources/virtualization/qemu/block/trace.h

`trace.h` is a one-line local include shim:

```c
#include "trace/trace-block.h"
```

It lets block-layer C files include `"trace.h"` locally while resolving to the generated block trace header. It contains no state, declarations, or logic of its own.
