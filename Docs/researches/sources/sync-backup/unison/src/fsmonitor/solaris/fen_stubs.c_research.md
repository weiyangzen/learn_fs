# sources/sync-backup/unison/src/fsmonitor/solaris/fen_stubs.c

Purpose: OCaml C bindings for Solaris/illumos file event notification via event ports.

Important APIs: `unsn_port_create`, `unsn_port_close`, `unsn_port_associate`, `unsn_port_reassociate`, `unsn_port_dissociate`, `unsn_port_get`, and `unsn_free_event_object`. `event_obj` stores a cookie, previous event mask, and `struct file_obj`.

Control flow: association allocates an `event_obj`, stores a duplicated path in `fo_name`, and calls `port_associate` with follow/no-follow event masks. Events are one-shot; `unsn_port_get` queries event count, allocates an event array, converts `PORT_SOURCE_FILE` events to OCaml tuples including port, event object pointer, cookie, and decoded flags. Reassociation returns false rather than raising for disappeared paths.

State/persistence: holds malloc-managed event objects that remain valid while associated. The OCaml side must free after event or dissociation. Kernel event-port registrations are mutated.

Dependencies/integration: Solaris `<port.h>`, file event flags, OCaml runtime, and the Solaris watcher implementation.

Risks: raw pointers are encoded as OCaml immediate-like values without custom finalizers, so misuse can cause double free/use-after-free. Comments call out this tradeoff. Event loss around recursive deletes is handled by false reassociation, not guaranteed delivery.

Test signals: tests should cover associate/get/reassociate/dissociate/free lifecycles, deleted-path reassociation, no-follow behavior, event flag decoding, and memory tooling for pointer lifecycle mistakes.
