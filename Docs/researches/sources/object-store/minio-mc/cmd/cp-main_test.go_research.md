# sources/object-store/minio-mc/cmd/cp-main_test.go

Purpose: Unit tests for copy metadata parsing.

Important APIs/types/functions: `TestParseMetaData`.

Control flow: Table cases call `getMetaDataEntry`, then compare returned maps and error causes. Success cases cover semicolon-separated entries, values containing `=`, `Cache-Control`, quoted values with embedded semicolons/quotes, and quoted keys. Failure cases cover missing `=`, wrong delimiter, and unterminated quote states.

State and persistence: No I/O or persistent state.

Dependencies/integration: Uses `reflect.DeepEqual` and Go `testing`.

Risks: Does not test empty key names, duplicate keys, whitespace trimming, Unicode, or integration with actual `mc cp --attr`.

Test signals: Good focused regression coverage for the custom state-machine parser.
