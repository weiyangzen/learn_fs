# File Research: sources/os/plan9/9front/sys/src/cmd/aux/listen.c

Role: Service-directory network listener manager for Plan 9.

High-level behavior:
- Scans service directories for executable files named with the selected protocol prefix, default `tcp`.
- Announces network addresses of the form `<proto>!<addr>!<service-suffix>`, default addr `*`.
- For each accepted call, forks a child, accepts the data connection, binds it to `/dev/cons`, duplicates it to stdin/stdout, and execs the service program with arguments `serv proto dir`.

Trust model:
- `-d` service directory runs as user `none` with a new namespace.
- `-t` trusted service directory runs in the invoker namespace.
- Optional per-service `.namespace` files can build namespaces for untrusted services.

Options:
- `-i` immutable service set, no periodic rescan.
- `-q` quiet, `-n namespace`, `-p maxprocs`, `-a addr`, `-o` connection control options, `-O` announce control options.
- Default connection control option is `keepalive`.

Process management:
- Maintains an announcement list, restarts failed announcers after waits, suppresses repeated address-in-use logs, and can throttle accepted child count with `maxprocs`.

Security and environment:
- Uses rfork flags to isolate fd, env, name, note, rendezvous groups for call children.
- `becomenone` calls `procsetuser("none")` and `newns`.
