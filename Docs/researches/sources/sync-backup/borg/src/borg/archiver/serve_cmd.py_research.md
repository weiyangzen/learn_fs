# sources/sync-backup/borg/src/borg/archiver/serve_cmd.py

Purpose: defines `ServeMixIn`, the CLI implementation for `borg serve`. It supports two transport/server modes: legacy Borg 1.x RPC serving through `RepositoryServer(...).serve()`, and current repository serving through `borgstore.server.rest.serve(..., stdio=True)` for `rest://` repositories.

Important APIs: `do_serve(args)` dispatches on `args.rest`; `do_serve_rest(args)` validates `--backend`, resolves permission mode from `--permissions` or `BORG_REPO_PERMISSIONS`, converts it through `repository.borg_permissions`, and launches the REST server; `check_rest_restrictions(backend, restrict_to_paths, restrict_to_repositories)` enforces path allowlists for `FILE:` backends; `build_parser_serve(...)` installs the subcommand and options.

Control flow and state: the legacy branch intentionally does not forward `args.permissions`, because Borg 1.x repositories have no permission system. REST mode requires a `FILE:<path>` backend and runs over stdio; it does not persist state itself, but it gates access before repository/server code takes over.

Dependencies and integration: integrates with `legacy.remote.RepositoryServer`, `borgstore.server.rest`, repository permission parsing, `PathNotAllowed`, and Borg's custom `ArgumentParser`. The restriction logic normalizes paths with `expanduser` and `realpath`, then compares trailing-slash-normalized prefixes or exact repository paths.

Risks: the restriction check only applies to `FILE:` backends; non-file backends with restrictions are rejected. Prefix comparison is deliberately strict for `--restrict-to-repository` and broad for `--restrict-to-path`; regressions here could create repository escape or over-blocking bugs. Permissions default to `"all"`, so deployments relying on environment configuration should verify `BORG_REPO_PERMISSIONS`.

Test signals: useful tests should cover REST without `--backend`, restriction pass/fail for subdirectories and exact repository paths, non-`FILE:` backend rejection, permission source precedence, and legacy mode not receiving REST-only permissions.
