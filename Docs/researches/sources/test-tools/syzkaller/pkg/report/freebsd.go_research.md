# sources/test-tools/syzkaller/pkg/report/freebsd.go

Purpose: Implements FreeBSD crash detection and parsing patterns.

Important APIs and data: `freebsd` wraps config. `ctorFreebsd` returns the reporter. Methods `ContainsCrash`, `Parse`, and `Symbolize` implement reporter behavior. `freebsdStackParams` is an empty stack-parameter set. `freebsdOopses` includes fatal trap and panic patterns, Go runtime errors, and common oopses.

Control flow: `ContainsCrash` delegates to `containsCrash` using FreeBSD oopses and ignores. `Parse` delegates to `simpleLineParser` with FreeBSD stack params. `Symbolize` is currently a no-op. Oops regexes extract titles from fatal traps, KDB stack backtraces, destroyed locks, SCTP/socket panics, ASan invalid access, and other known FreeBSD panic messages.

State and persistence: No persistent state beyond reporter config.

Dependencies and integration: Registered by the report package for FreeBSD targets. Uses common report parser utilities and regex helpers.

Risks: No symbolization means title quality relies on regex extraction. Regexes are specific to known FreeBSD log formats and can miss new panic variants. Generic common oopses may classify unexpected runtime failures.

Test signals: No direct FreeBSD-specific tests in this shard; general report parser tests elsewhere likely cover fixtures.
