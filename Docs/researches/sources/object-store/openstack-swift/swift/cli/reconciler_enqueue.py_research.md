# sources/object-store/openstack-swift/swift/cli/reconciler_enqueue.py

Purpose: debugging/development CLI to manually enqueue a misplaced object operation for the container reconciler.

Important APIs: module-level `parser` and `main()`. `main()` parses policy index, full `/a/c/o` path, timestamp, operation `PUT`/`DELETE`, and `--force`.

Control flow: enables eventlet hub exception debugging, parses args, loads the container ring from `/etc/swift/container.ring.gz`, resolves the policy by index, validates and splits the object path, then calls `add_to_reconciler_queue()`. It prints the reconciler container name on success and returns error strings for invalid policy, invalid path, or failed enqueue.

State and persistence: writes to the reconciler queue through container-ring placement via `add_to_reconciler_queue()`. It does not touch object data directly.

Dependencies and integration: depends on `Ring`, `POLICIES`, `split_path`, eventlet, and `swift.container.reconciler`.

Risks: hard-coded `/etc/swift/container.ring.gz` limits testability and alternate deployments. Manual enqueue with wrong policy/timestamp/op can cause reconciler churn or incorrect repair attempts. Tests should mock policy lookup, path parsing, queue insertion, force behavior, invalid args, and error return strings.
