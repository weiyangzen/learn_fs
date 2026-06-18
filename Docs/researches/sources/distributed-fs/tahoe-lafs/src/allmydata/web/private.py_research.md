# sources/distributed-fs/tahoe-lafs/src/allmydata/web/private.py

## Purpose
Builds the authenticated `/private` resource tree for node-local private WebAPI features. It implements a custom Tahoe-LAFS HTTP authorization scheme based on the node's `api_auth_token`, currently protecting the private log-streaming subtree.

## Important APIs, Types, And Functions
`IToken` is the credentials interface. `Token` stores the proposed token and compares it with `timing_safe_compare`. `TokenChecker` validates credentials against `get_auth_token`. `TokenCredentialFactory` defines scheme `tahoe-lafs` and decodes authorization bytes. `PrivateRealm` returns the protected resource root for `IResource`. `_create_vulnerable_tree` installs `logs`, `_create_private_tree` wraps it in `HTTPAuthSessionWrapper`, and `create_private_tree` is the public constructor.

## Control Flow
`root.Root` calls `create_private_tree(client.get_auth_token)` and mounts the result at `/private`. Twisted Web guard parses the `Authorization` header using `TokenCredentialFactory`, passes a `Token` to `TokenChecker`, and, on success, asks `PrivateRealm` for the wrapped resource. The vulnerable tree is only reachable through this wrapper and currently exposes `logs/v1`.

## State And Persistence
The module stores no durable state. `TokenChecker` holds a callable used to fetch the current auth token on each login attempt. `Token` instances hold request-local proposed tokens. The protected tree holds child resources such as log streaming.

## Dependencies And Integration Points
It depends on `attrs`, Zope interfaces, Twisted cred/guard/resource interfaces, Tahoe timing-safe comparison and precondition helpers, and `logs.create_log_resources`. It integrates directly with `root.py` and indirectly with `logs.py` for private WebSocket access. Tests are in `src/allmydata/test/web/test_private.py` and `test_logs.py`.

## Risks And Test Signals
Security depends on correct Twisted credential parsing and constant-time token comparison. The token is accepted as raw bytes after the `tahoe-lafs` scheme, so tests should include missing, wrong, and correct Authorization headers. `_create_vulnerable_tree` is deliberately named to show it must remain wrapped. Useful test signals include scheme challenge, unauthorized login failures, successful resource traversal, no accidental exposure of `/private/logs` through the public root, and token type preconditions.
