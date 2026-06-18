# sources/sync-backup/syncthing/internal/gen/apiproto/tokenset.pb.go

## Purpose
This generated protobuf file defines the API-facing `TokenSet` message.

## Important APIs and Types
`TokenSet` is a generated message with one field, `Tokens map[string]int64`, documented as token string to expiry time in epoch nanoseconds. Standard generated methods include `Reset`, `String`, `ProtoMessage`, `ProtoReflect`, deprecated `Descriptor`, and `GetTokens`. The file also exposes `File_apiproto_tokenset_proto`, raw descriptor data, message info, Go type metadata, dependency indexes, and an init-time `protoimpl.TypeBuilder`.

## State and Persistence Behavior
Runtime state is message data plus protobuf reflection descriptor caches. The map values encode expiry timestamps as int64 nanoseconds; interpretation and validation are performed by callers, not this generated file.

## Dependencies and Integration Points
It depends on `google.golang.org/protobuf/reflect/protoreflect`, `runtime/protoimpl`, `reflect`, and `sync`. It is generated from `apiproto/tokenset.proto` and should not be hand-edited.

## Risks and Test Signals
Generated code risk is schema drift: callers depend on field number 1 and map key/value encoding remaining stable. There are no local tests in this subset; validation should be through protobuf regeneration and API token tests elsewhere.
