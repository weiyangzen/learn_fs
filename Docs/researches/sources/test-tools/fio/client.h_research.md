## sources/test-tools/fio/client.h

Purpose: public interface and state model for fio's client-side network controller.

Important APIs and types: defines client states (`Client_created` through `Client_exited`), `struct client_file`, `struct fio_client`, callback typedefs, `struct client_ops`, `struct client_eta`, address type enum, client type enum, exported lifecycle functions, option/job-file senders, reply wait/update helpers, trigger sender, and global aggregate stats (`sum_stat_clients`, `client_ts`, `client_gs`).

State and persistence: `struct fio_client` is the central mutable object: list/hash links, address union, hostname/port/fd/refs, output and JSON option state, job counters, command args, files, ETA tracking, pending replies, state/error/signal, and caller-owned `client_data`.

Dependencies and integration: includes socket headers, `lib/types.h`, and `stat.h`. Callers provide `client_ops` callbacks so CLI and GUI frontends can share transport logic while customizing output and timeout behavior.

Risks and test signals: the header exposes many fields directly, increasing coupling to `client.c` internals. Any change to client state or callbacks needs consumers rebuilt and tested against both CLI and GUI paths. Compilation of downstream users is the first signal; multi-client run behavior validates semantics.
