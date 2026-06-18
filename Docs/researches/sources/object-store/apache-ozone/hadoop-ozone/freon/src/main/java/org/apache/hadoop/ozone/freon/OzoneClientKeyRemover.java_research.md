## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OzoneClientKeyRemover.java

Purpose: Freon subcommand `ockr`/`ozone-client-key-remover` that deletes generated keys through the Ozone client API.

Important APIs/types/functions: options configure volume, bucket, and OM service ID. `call` obtains target `OzoneBucket`, creates `remove` timer, and runs `removeKey`; `removeKey` deletes `generateObjectName(counter)`.

Control flow: initialize Freon, create Ozone client, get volume/bucket, run timed deletes, close client through try-with-resources.

State and persistence behavior: deletes Ozone key metadata/data references in the target bucket. Local state stores bucket handle and timer.

Dependencies and integration points: paired with `OzoneClientKeyGenerator`; uses Ozone object store APIs.

Risks: fails on missing keys; does not ensure bucket existence; delete semantics may be asynchronous with respect to physical block cleanup.

Test signals: removed keys should no longer be readable/listed; timer count should match deletes.
