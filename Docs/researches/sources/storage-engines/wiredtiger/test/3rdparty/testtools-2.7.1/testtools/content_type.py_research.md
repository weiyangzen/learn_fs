# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/content_type.py

Purpose: small representation of MIME content types used by testtools details.

Important APIs, types, and functions: `ContentType(primary_type, sub_type, parameters=None)` stores `type`, `subtype`, and parameter dict, implements equality against the same class, and formats as `type/subtype; key="value"`. Constants `JSON` and `UTF8_TEXT` represent `application/json` and `text/plain; charset="utf8"`.

Control flow: construction rejects `None` primary or subtype. `__repr__` sorts parameters for stable output.

State and persistence: state is immutable-by-convention object attributes, though `parameters` remains a mutable dict if callers mutate it. No persistence.

Dependencies and integration points: used by `testtools.content` and result serialization code to classify diagnostic payloads.

Risks and test signals: equality is strict on exact class type, not duck-typed subclasses. Mutable `parameters` can change repr/equality after construction. Test signals are content equality, repr stability, and text decoding by charset parameter.
