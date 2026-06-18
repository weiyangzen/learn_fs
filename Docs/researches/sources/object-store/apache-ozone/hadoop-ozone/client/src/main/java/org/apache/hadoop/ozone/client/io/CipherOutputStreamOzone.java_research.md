# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/CipherOutputStreamOzone.java

Purpose: This is a small Ozone-specific wrapper around `javax.crypto.CipherOutputStream` that preserves access to the wrapped stream and forwards key metadata operations through encryption.

Important APIs and types: The public API is the constructor taking `OutputStream` and `Cipher`, the protected constructor for subclasses/tests, `getWrappedStream`, and `getMetadata`. It implements `KeyMetadataAware` and depends on the wrapped stream also implementing that interface.

Control flow: Construction delegates to `CipherOutputStream` and stores the original output stream. Metadata requests unwrap one level and cast the wrapped stream to `KeyMetadataAware`.

State and persistence behavior: It stores only the wrapped stream reference. Persistence is delegated to the downstream key output stream, including metadata and commit behavior.

Dependencies and integration points: `OzoneOutputStream` and `OzoneDataStreamOutput` know how to unwrap this class, similar to Hadoop `CryptoOutputStream`, so encrypted outputs still expose commit metadata and pre-commit hooks.

Risks: `getMetadata` can throw `ClassCastException` if the wrapped stream is not `KeyMetadataAware`. The `output` field is not final even though it behaves as immutable after construction.

Test signals: Tests should cover metadata passthrough through cipher wrapping, wrapped-stream identity, close/write delegation inherited from `CipherOutputStream`, and failure behavior when wrapping an incompatible stream.
