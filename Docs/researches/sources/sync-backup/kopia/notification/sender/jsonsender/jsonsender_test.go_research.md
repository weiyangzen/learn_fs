# sources/sync-backup/kopia/notification/sender/jsonsender/jsonsender_test.go

Purpose: verifies JSON sender severity filtering and output format.

Important APIs/types/functions: `TestJSONSender`, `jsonsender.NewJSONSender`, `notification.SeverityWarning`, `sender.Message`, and a `bytes.Buffer` output sink.

Control flow: the test creates a JSON sender with prefix `NOTIFICATION:` and warning threshold, sends verbose, warning, and error messages, trims/splits the buffer by newline, and asserts only warning/error messages were encoded as prefixed JSON.

State and persistence behavior: all state is in the local buffer. The ignored low-severity message confirms no output side effect for filtered messages.

Dependencies/integration points: exercises the JSON serialization shape of `sender.Message` and the severity constants from the higher-level notification package. Risks/test gaps include no writer-error coverage, no concurrent send coverage, and no message headers in the encoded samples. The exact expected JSON strings are useful signals for field names and omitted empty fields.
