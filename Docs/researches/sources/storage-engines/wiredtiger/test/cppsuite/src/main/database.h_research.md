# sources/storage-engines/wiredtiger/test/cppsuite/src/main/database.h

Purpose: Declares the cppsuite database model, a thread-safe map of collection ids to collection metadata plus creation/tracking configuration.

Important APIs/types/functions: public API covers collection creation, seeding existing collections, lookup/random selection, collection count/name/id listing, and dependency/config setters.

Control flow: callers configure create options and dependency pointers before adding collections; workload operations query the model during execution.

State and persistence: holds create config string, timestamp manager pointer, operation tracker pointer, next id, collection map, and mutex. Persistent table creation is implemented in the source file.

Dependencies/integration: includes `collection` and `operation_tracker`; used by workload manager, database operations, metrics, and validators.

Risks and test signals: pointer dependencies are non-owning and asserted to be set only once. Model and persistent database can diverge if table creation succeeds but later model/tracking assumptions fail; tests rely on validation and operation tracking to catch that.
