# sources/object-store/openstack-swift/swift/common/middleware/crypto/__init__.py

## Purpose
`crypto/__init__.py` is the PasteDeploy entry point for Swift object encryption middleware. It composes the write-side `Encrypter` and read-side `Decrypter` into a single `encryption` filter.

## Important APIs, Types, and Functions
`filter_factory(global_conf, **local_conf)` merges config, registers encryption capability data in Swift info, and returns `encryption_filter(app)`, which constructs `Decrypter(Encrypter(app, conf), conf)`.

## Control Flow
At load time, the factory computes `enabled` from `disable_encryption` and publishes `register_swift_info('encryption', admin=True, enabled=enabled)`. At pipeline construction, the returned closure wraps the downstream app with `Encrypter`, then wraps that with `Decrypter`, making decryption the outermost crypto component for client responses.

## State and Persistence
This file has no persistent state. It passes configuration to the two crypto middlewares, which persist encryption metadata through object sysmeta/transient sysmeta.

## Dependencies and Integration Points
It depends on `Decrypter`, `Encrypter`, `config_true_value`, and Swift registry. It must be paired with a keymaster middleware earlier in the pipeline so crypto contexts can call `swift.callback.fetch_crypto_keys`.

## Risks and Edge Cases
Disabling encryption only disables new writes in `Encrypter`; the `Decrypter` remains necessary for existing encrypted data. Pipeline order relative to keymaster, copy, SLO/DLO, and gatekeeper is security-sensitive.

## Test Signals
Tests should cover factory composition order, info registration for enabled and disabled states, config merging, and continued read/decrypt behavior when `disable_encryption` is true.
