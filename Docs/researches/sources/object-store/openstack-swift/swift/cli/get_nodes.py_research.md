# sources/object-store/openstack-swift/swift/cli/get_nodes.py

Purpose: command-line wrapper that shows which storage nodes own a Swift account, container, object, or raw partition.

Important APIs: `main()` only; core parsing and printing are delegated to `swift.cli.info.parse_get_node_args()` and `print_item_locations()`.

Control flow: parses `--all`, `--partition`, `--policy-name`, `--swift-dir`, and `--quoted`. It sets the Swift directory and reloads storage policies when needed, validates ring/path arguments, optionally loads a ring from a `.ring.gz` file, derives ring name from the filename, and prints locations. `InfoSystemExit` is converted into help text plus an error or exit code.

State and persistence: read-only; it loads local ring files and storage-policy config.

Dependencies and integration: depends on `Ring`, storage-policy reload, and `info.py` helper functions. It is a thin console entry point for ring placement inspection.

Risks: output is only as current as local ring files. Passing the wrong ring with a path type can produce warnings or misleading operator commands. Tests should cover quoted path parsing, policy-name object lookup, partition lookup, invalid ring paths, handoff inclusion, and error exits.
