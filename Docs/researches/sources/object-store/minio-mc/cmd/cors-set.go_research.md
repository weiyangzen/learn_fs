# sources/object-store/minio-mc/cmd/cors-set.go

Purpose: Implements `mc cors set` and the shared output message type for all CORS subcommands.

Important APIs/types/functions: `corsSetCmd`, `corsMessage`, `String`, `JSON`, `checkCorsSetSyntax`, and `mainCorsSet`.

Control flow: Requires `ALIAS/BUCKET CORSFILE`. The CORS file is read from a named file or stdin when `-` is used. It initializes a client and calls `SetBucketCors(globalContext, corsXML)`. `corsMessage.String` emits raw XML for get, success text for set/remove, and a not-found message for nil config.

State and persistence: Reads a local XML file/stdin and writes remote bucket CORS configuration.

Dependencies/integration: Uses `minio-go` CORS config, colorjson, console, and probe errors.

Risks: Local XML is passed to the client without pre-validation here. `String` fatals if converting returned CORS config to XML fails.

Test signals: No direct tests.
