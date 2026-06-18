# sources/object-store/openstack-swift/doc/saio/swift/internal-client.conf

## Purpose
Defines an internal Swift proxy client pipeline for daemons that need to issue cluster requests without using the public proxy config.

## Important Sections
Pipeline is `catch_errors proxy-logging cache symlink keymaster encryption proxy-server`. The proxy app enables `account_autocreate` and account management. Keymaster uses a placeholder `encryption_root_secret`; encryption and symlink middleware are enabled.

## Control Flow and Integration
Container sync, sharder, expirer, and other internal clients can load this pipeline to perform internal object/account/container operations. Middleware order ensures errors/logging/cache, symlink handling, keymaster, encryption, then proxy app.

## State, Risks, and Test Signals
State changes are remote Swift requests; local persistence is only middleware cache/log effects. Placeholder encryption secret is a security risk outside SAIO. Test signal is successful daemon internal requests, especially encrypted/symlink object handling.
