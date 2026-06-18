<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/tls.rs -->
# sources/object-store/rustfs/crates/config/src/constants/tls.rs

## Purpose
Defines TLS, mTLS, HTTP/2, HTTP/1, and certificate hot-reload environment names and defaults.

## Important APIs, types, and functions
Security constants include TLS key logging, trust system CA, trust leaf cert as CA, default client CA/cert/key filenames, mTLS client cert/key envs, and server mTLS enable default false. Transport tuning covers HTTP/2 stream/connection window, frame/header size, max concurrent streams, keepalive interval/timeout, HTTP/1 header timeout and buffer size. Reload constants default disabled with 30-second interval.

## Control flow
No local execution; TLS and HTTP server/client builders consume these constants.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with rustls/native cert trust, mTLS authentication, HTTP/2 and HTTP/1 server transport configuration, and certificate reload watchers.

## Risks and edge cases
TLS key logging and trust-leaf-as-CA are high-risk debug/compatibility features and default off. HTTP/2 limits must remain within protocol bounds. Hot reload disabled by default avoids watcher complexity but requires restart for cert rotation unless enabled.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. TLS tests should cover cert path defaults, mTLS enablement, trust settings, HTTP/2 bounds, HTTP/1 header timeout, and reload interval minimums.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/tls.rs -->
