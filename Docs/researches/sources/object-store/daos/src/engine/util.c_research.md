# sources/object-store/daos/src/engine/util.c

Purpose: server utility file currently providing registration of native DAOS dbtree classes used by server modules.

Important APIs and functions: `dss_register_dbtree_classes()` registers `DBTREE_CLASS_KV`, `DBTREE_CLASS_IV`, `DBTREE_CLASS_IFV`, `DBTREE_CLASS_NV`, `DBTREE_CLASS_UV`, and `DBTREE_CLASS_EC` with their operation tables and feature flags.

Control flow: registration is sequential. On the first `dbtree_class_register()` failure, it logs the class-specific failure and returns the error. There is no rollback for classes already registered.

State and persistence: modifies process-global dbtree class registry state. The comment explicitly notes unregistering is currently unsupported. There is no file persistence.

Dependencies and integration: depends on DAOS btree class APIs and operation tables (`dbtree_kv_ops`, `dbtree_iv_ops`, `dbtree_ifv_ops`, `dbtree_nv_ops`, `dbtree_uv_ops`, `dbtree_ec_ops`). Included headers also tie the file to server internals, dRPC internals, placement, TLS, and telemetry, though this function only uses dbtree registration and logging.

Risks: partial registration can remain after a later class fails because no unregister path exists. Repeated calls may depend on dbtree registry semantics for duplicate registration. The broad include set can hide unnecessary coupling and rebuild impact.

Test signals: startup or module-init tests should expect all classes registered once and clear error logs identifying the failed class if registration fails.
