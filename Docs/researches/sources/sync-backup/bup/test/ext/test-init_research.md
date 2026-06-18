## sources/sync-backup/bup/test/ext/test-init

Purpose: tests repository initialization argument precedence and remote init.

Important control flow: verifies commands fail against an uninitialized `-d` repo, initializes via `-d repo`, positional repo argument, positional overriding `-d`, positional overriding `BUP_DIR`, and `bup init --remote -:repo`. It also asserts initializing `/dev/null` fails with the generic failure code.

State and dependencies: creates/removes temp repos and inspects `refs/heads` and `objects/pack`.

Risks covered: init destination precedence, environment interaction, remote URL handling, and failure on invalid repo path.
