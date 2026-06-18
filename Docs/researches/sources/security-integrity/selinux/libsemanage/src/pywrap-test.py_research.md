# sources/security-integrity/selinux/libsemanage/src/pywrap-test.py

Purpose: manual/smoke test driver for the Python semanage bindings. It can list and optionally modify modules, users, seusers, ports, fcontexts, interfaces, booleans, active booleans, and nodes.

Important types/functions: custom `Usage`, `Status`, and `Error` exceptions; `Tests` selection state; read tests such as `test_modules`, `test_users`, `test_ports`, `test_fcontexts`, `test_interfaces`, `test_booleans`, `test_abooleans`, `test_nodes`; write tests for user/seuser/port/fcontext/interface/boolean/active boolean/node; and `main` option parsing/handle lifecycle.

Control flow: `main` parses short and long options, creates a semanage handle, checks managed status, connects, dispatches selected tests, disconnects, and destroys the handle. Read tests list records and print selected fields. Write tests create a record, save an existing local value if present, begin a transaction, modify and commit, begin a second transaction, then delete or restore the old value and commit again.

State/persistence: read tests inspect policy/local/active state. Write tests intentionally mutate the semanage store and active boolean state, then try to restore. Dependencies are the generated `semanage` Python module and a managed SELinux system.

Risks: script returns `2` even after successful execution because `main` always returns 2; write tests can affect real policy if restore fails; option string and long option names are uneven. Test signals are primarily manual binding coverage, not hermetic CI. Safer tests should run in an isolated store/root.
