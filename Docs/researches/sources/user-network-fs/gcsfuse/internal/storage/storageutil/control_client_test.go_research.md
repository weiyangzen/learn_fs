## sources/user-network-fs/gcsfuse/internal/storage/storageutil/control_client_test.go

Purpose: Tests `CreateGRPCControlClient` call-option behavior.

Important APIs/types/functions: `ControlClientTest` creates unauthenticated control clients and asserts `CallOptions` for Create/Get/Delete/Rename folder APIs.

Control flow: one test requests normal GAX retries and expects non-empty call-option slices; another requests disabled defaults and expects empty slices if `CallOptions` is present.

State and persistence behavior: constructing the client mutates the direct-path environment internally; the test does not explicitly check cleanup.

Dependencies and integration points: depends on Google generated control client defaults and `option.WithoutAuthentication`.

Risks: tests may be brittle across Google client library changes to default call options. They do not cover client construction error cleanup.

Test signals: confirms the key behavior used by storage retry wrappers: raw clients can be created with or without generated retry policy.
