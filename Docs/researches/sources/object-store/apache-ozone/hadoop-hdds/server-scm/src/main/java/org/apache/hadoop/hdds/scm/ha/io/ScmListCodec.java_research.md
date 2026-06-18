# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmListCodec.java

Purpose: SCM HA codec for Java `List` arguments and return values.

Important APIs and types: Encodes lists into `SCMRatisProtocol.ListArgument` containing an element type name and repeated serialized element bytes. Uses `ScmCodecFactory.ClassResolver` and element codecs.

Control flow: Serialization rejects non-list objects, uses a special empty-list encoding with `Object` type, otherwise resolves the first element's class and serializes each element with that codec. Deserialization parses `ListArgument`, validates type, resolves the element class, deserializes each element, and returns `ArrayList<Object>`.

State and persistence behavior: Stateless apart from resolver reference; bytes are part of Ratis messages.

Dependencies and integration points: Needed for secret keys, certificate lists, deleted-block transaction lists, and other generated invoker list return values.

Risks and test signals: Empty lists lose concrete element type, and mixed-type lists are unsafe because the first element determines the codec. Tests should cover empty list, homogeneous supported lists, malformed argument bytes, unsupported element classes, and mixed-list failure or documented behavior.
