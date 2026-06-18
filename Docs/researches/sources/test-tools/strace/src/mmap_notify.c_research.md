<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mmap_notify.c -->
# sources/test-tools/strace/src/mmap_notify.c

Purpose: implements a small notification fanout for memory-map changes.
Important APIs/types/functions: `mmap_notify_register_client`, `mmap_notify_report`, callback list storage, and `mmap_notify_client` structures.
Control flow: registration appends a callback/data pair; reporting iterates registered clients and invokes callbacks for the affected `tcb`. State and persistence behavior: process-global client list persists for the strace lifetime.
Dependencies and integration points: mmap cache invalidation and any other mapping-change consumers. Risks: callback order and lifetime ownership are simple but not thread-safe. Test signals: register multiple clients and verify all receive mmap/munmap notification events.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mmap_notify.c -->
