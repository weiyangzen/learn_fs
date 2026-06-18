# sources/object-store/rustfs/crates/iam/src/lib.rs

The IAM crate root declares public modules and owns global IAM/OIDC runtime initialization. It exposes `cache`, `error`, `keyring`, `manager`, `oidc`, `oidc_state`, `store`, `sys`, and `utils`, plus two `OnceLock` singletons: `IAM_SYS: Arc<IamSys<ObjectStore>>` and `OIDC_SYS: Arc<OidcSys>`.

`init_iam_sys` is the main async initializer. It returns `Ok(())` if IAM is already initialized, otherwise logs startup, creates an `ObjectStore` from `Arc<ECStore>`, awaits `IamCache::new` for initial persistent load, constructs `IamSys`, and stores it. `get` returns the singleton or `IamSysNotInitialized`, with a defensive `is_ready` check. `init_oidc_sys` initializes OIDC and installs an empty OIDC system on non-fatal provider initialization failure; `get_oidc` returns the optional singleton.

State is process-global and one-shot, with no reset path. Integration points include ECStore, IAM object store, cache manager, `IamSys`, `OidcSys`, and tracing. Risks are inability to reinitialize in one process and non-fatal OIDC failures being visible only through logs unless monitored.
