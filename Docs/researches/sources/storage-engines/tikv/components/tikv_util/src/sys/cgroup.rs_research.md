# sources/storage-engines/tikv/components/tikv_util/src/sys/cgroup.rs

## Purpose
Detects Linux cgroup v1/v2 limits for memory, CPU quota, and cpuset cores, including container mount-root path reconstruction from `/proc/self/mountinfo`.

## Important APIs, Types, and Functions
- `CGroupSys::new` reads `/proc/self/cgroup`, detects unified v2 mode via `statfs`, parses cgroup paths, and parses cgroup mount points.
- `memory_limit_in_bytes`, `cpuset_cores`, and `cpu_quota` read controller files and return optional/empty limits.
- Parsers include `parse_proc_cgroup_v1/v2`, `parse_mountinfos_v1/v2`, `build_path`, `parse_memory_max`, `parse_cpu_cores`, `parse_cpu_quota_v1/v2`, and `capping_parse_int`.

## Control Flow
Construction branches on v1/v2. v1 maps individual controllers such as `memory`, `cpuset`, and `cpu`; v2 uses the empty controller name. Limit queries look up the process cgroup path and mounted root, reconstruct an accessible absolute path, then read the appropriate controller file. Numeric parsing treats `"max"` or negative/unlimited values as no limit and caps integer overflow to type bounds where intended.

## State and Persistence Behavior
`CGroupSys` snapshots cgroup path and mount-point mappings at construction. Actual limit files are read when query methods run. No durable state is written.

## Dependencies and Integration Points
Depends on `procfs`, `libc::statfs`, filesystem reads, `num_traits::Bounded`, and `config::normalize_path`. `sys/mod.rs` keeps a lazy static `SELF_CGROUP` and also offers current re-read variants.

## Risks
Container mount layouts are complex; `build_path` can fail when cgroup paths do not align with mount roots. Missing mount points or file read errors return no limit/empty cpuset after logging. Parsing intentionally tolerates malformed values, which can hide configuration issues. The manual cgroup integration test requires privileged cgroup tools and is feature-gated.

## Test Signals
Tests cover default no-limit behavior, mountinfo parsing with and without cgroups, cgroup v1/v2 parsing, relative/conflicting mount roots, missing mountinfo, memory max parsing including overflow/malformed input, cpuset parsing, CPU quota parsing, cgroup paths containing colons, and a feature-gated live cgroup test.
