# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/SecurityConstants.java

## Purpose
Defines RFC-7468 PEM boundary labels and pre/post encapsulation strings for public and private keys.

## Important APIs and types
Constants include `PEM_ENCAPSULATION_BOUNDARY_LABEL_PUBLIC_KEY`, `PEM_ENCAPSULATION_BOUNDARY_LABEL_PRIVATE_KEY`, and their full `-----BEGIN ...-----` / `-----END ...-----` forms.

## Control flow and state
There is no mutable state or control flow. The private constructor prevents instantiation.

## Dependencies and integration points
`KeyCodec` uses the labels when encoding PEM key objects. Other security code can use the full boundary strings for validation or parsing.

## Risks and test signals
Tests should only be needed where consumers depend on exact PEM labels. Changing these strings breaks compatibility with existing key files.
