## sources/sync-backup/bup/test/ext/test-help

Purpose: verifies top-level and command-specific help dispatch.

Important control flow: checks `bup -?`, `bup -h`, and `bup --help` print usage. If generated manpage `Documentation/bup-save.1` exists, it creates a temporary `MANPATH`, runs `bup help save` and `bup save --help` through `PAGER=cat`, and checks expected save help text.

State and dependencies: temp repo environment, optional documentation/manpage files, `man`/pager behavior.

Risks covered: launcher/main dispatch, help aliases, and installed documentation lookup.
