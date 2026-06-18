# File Research: sources/local-fs/squashfs-tools/squashfs-tools/process_fragments.h

Public header for fragment processing.

Exports:
- `frag_thrd(void *)`

Role:
- Lets the main mksquashfs thread create fragment-processing worker threads.

Notes:
- The worker expects global queues/caches and destination-file context to have been initialized elsewhere.
