# File Research: sources/os/plan9/9front/sys/src/cmd/aux/listen1.c

`listen1` is a single-service network listener. It announces an address, accepts calls, optionally forks per connection, binds the accepted connection to `/dev/cons`, duplicates it to stdin/stdout, sets `net` to the connection directory, and execs the requested command.

Key controls are `-1` one-shot/no child fork, `-t` trusted mode skipping `becomenone`, `-v` preserving stdout, `-p` process limit with `/proc/$pid/wait` backpressure, `-n` namespace file, `-O` listener ctl options, and `-o` connection ctl options. By default it becomes user `none` and installs a new namespace before announcing.

Notable implementation details: default connection option is `keepalive`; stderr remains attached to the original process; `remoteaddr` reads `<netdir>/remote` and strips service after `!`; overload during fork failure rejects the call with `host overloaded`.
