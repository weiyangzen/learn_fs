# sources/storage-engines/tikv/components/test_raftstore/src/config.rs

Purpose: this file wraps `TikvConfig` for tests so each cluster gets an isolated temporary config path while preserving ergonomic access to TiKV configuration fields.

Important APIs, types, and functions: `Config` holds `cfg_dir: Option<TempDir>`, `tikv: TikvConfig`, and `prefer_mem: bool`. `Config::new()` creates a temp config directory, rewrites `tikv.cfg_path` to `<temp>/tikv.toml`, and stores the preference for memory-backed temp dirs. `Clone` deliberately drops `cfg_dir` while cloning the underlying TiKV config and `prefer_mem`. `Deref` and `DerefMut` expose `TikvConfig` fields directly.

Control flow: callers create a `Config` around a `TikvConfig` before passing it to cluster/node/server setup. When a config is cloned for node startup, the clone does not own a temp dir; the original cluster config keeps the temp directory alive.

State and persistence behavior: the temp config directory is the only owned state. It prevents online config writes from modifying `common-test.toml` or other shared files. Dropping cloned `cfg_dir` ownership avoids multiple `TempDir` handles attempting to represent the same persistent location.

Dependencies and integration points: it is used by both legacy and v2 harnesses. Because it dereferences to `TikvConfig`, existing code can pass `Config` into validation and engine path inference with minimal friction.

Risks and test signals: clones have `cfg_dir: None`, so code that needs the temp directory path must use the original `Config` or handle `None`. Helpers such as encryption setup rely on `cfg_dir` being present and should run before cloning into node/server startup.
