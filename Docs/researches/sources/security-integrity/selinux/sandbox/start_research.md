# sources/security-integrity/selinux/sandbox/start
# sources/security-integrity/selinux/sandbox/start

Purpose: minimal Python helper that runs one command string and prints output only on success.

Important APIs and control flow: imports `getstatusoutput`, initializes `rc`, attempts `getstatusoutput(sys.argv[1])`, suppresses exceptions, and prints captured stdout if exit status is zero.

State and persistence: no durable state; executes arbitrary command supplied as first argument.

Dependencies and integration points: used by `sandboxX.sh` to run `.sandboxrc` inside the graphical sandbox.

Risks and test signals: command is interpreted by the shell through `getstatusoutput`, so caller must supply trusted command content. Exceptions are swallowed, which hides failures. No direct tests.
