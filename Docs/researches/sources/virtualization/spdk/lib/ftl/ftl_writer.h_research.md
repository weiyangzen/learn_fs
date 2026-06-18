# File Research: sources/virtualization/spdk/lib/ftl/ftl_writer.h

Declares `struct ftl_writer` and writer APIs.

State includes the owning device, request queue, current and next bands, full-band queue, write limit threshold, halt flag, writer band type, last sequence ID, and optional padding request.

Exposed operations initialize the writer, run one scheduling pass, react to band state changes, halt/resume, check halted state, enqueue requests, and query free blocks.

Note: `ftl_writer_is_halted` and `ftl_writer_run` are declared twice in this header, which is harmless but redundant.
