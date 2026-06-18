# sources/storage-engines/wiredtiger/test/cppsuite/src/main/validator.cpp

## Purpose
Implements default cppsuite validation by replaying operation-tracking rows into an in-memory model and comparing that model with on-disk WiredTiger collections.

## Important APIs, Types, And Functions
Primary method is `validator::validate`. Helpers are `parse_schema_tracking_table`, `update_data_model`, `verify_collection`, `verify_collection_file_state`, and `verify_key_value`.

## Control Flow
Validation opens a session and operation tracking cursor, checks that the tracking table schema matches default expected key/value formats, parses schema tracking rows to build created/deleted collection lists, verifies deleted collections are absent, compares created collection ids with the database model, then walks the operation tracking table sorted by collection id. When the collection id changes, the current reconstructed map is verified against disk before processing the next collection.

## State And Persistence Behavior
The validator reads operation and schema tracking tables and table files but does not intentionally mutate them. It builds a `validation_collection` map from tracked keys to existence/value state. `DELETE_KEY` requires the key to exist and not already be deleted; `INSERT` creates or replaces the current model value.

## Dependencies And Integration Points
Depends on `logger`, `connection_manager`, `database`, standard containers, `tracking_operation`, and default operation-tracking schema constants. Called by `database_operation::validate` when operation tracking is enabled and the test has not supplied custom validation.

## Risks And Test Signals
Default validation aborts if a test uses a custom tracking schema, so such tests must override `validate`. The implementation assumes operation tracking rows are ordered by collection id and that dropping is not generally supported by the standard database model. It validates only tracked final state; missing tracker rows can make disk state appear valid incorrectly. Success is absence of `testutil_die`/assert failures after all collections and keys are checked.
