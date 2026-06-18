## sources/object-store/rustfs/crates/targets/src/sys/user_agent.rs

Purpose: constructs RustFS User-Agent strings that include platform, architecture, product version, and optional service type.

Important APIs/types/functions: `ServiceType` enumerates `Basis`, `Core`, `Event`, `Logger`, and `Custom(Cow<'static, str>)`. Internal `UserAgent` stores `os_platform`, `arch`, `version`, and service. `get_user_agent(service)` creates and formats the string as `Mozilla/5.0 (<platform>; <arch>) RustFS/<VERSION>` plus `(<service>)` for non-basis services.

Control flow and state: `OS_PLATFORM: OnceLock<String>` computes the platform once. OS-specific helpers use `sysinfo::System` for Windows/macOS/Linux, and fixed strings for BSD variants. The cached string is returned as `&'static str`.

Dependencies and integration points: depends on `rustfs_config::VERSION`, `std::env::consts::ARCH`, `OnceLock`, `Cow`, and `sysinfo` except OpenBSD. HTTP clients in target implementations can use this to identify service traffic.

Risks: platform detection is cached forever, which is correct for normal runtime but hard to override in tests. On unknown OSes it reports `Unknown`. Some OS helpers are compiled as `N/A` on other platforms and only selected by `cfg!`.

Test signals: tests verify basis omits `(basis)`, core/custom include service suffixes, version is present, and cached platform pointers are reused.
