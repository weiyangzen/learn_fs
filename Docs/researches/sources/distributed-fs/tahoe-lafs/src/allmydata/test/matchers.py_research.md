<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/matchers.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/matchers.py

Purpose: Defines `testtools` matchers for Tahoe-specific structures such as node public keys, storage announcements, fURLs, NURLs, base32 values, and equality between tuple elements.

Important APIs and types: `MatchesNodePublicKey` verifies a signing key against the private key stored in a node config. `matches_storage_announcement` builds a structural matcher for introducer storage announcements. `matches_furl`, `matches_nurls`, and `matches_base32` use preprocessing decoders with permissive `Always` matching. `MatchesSameElements` asserts a two-tuple has equal elements.

Control flow: Public-key matching reads node config, reconstructs the private key, signs empty bytes, derives the public key from the candidate key, and verifies the signature. Announcement matching composes `MatchesStructure` and `MatchesDict` with optional anonymous storage and plugin option fields.

State and persistence: Reads private node config from `basedir` at match time. No writes or persistent mutation.

Dependencies and integration points: Uses `attrs`, `hyperlink.DecodedURL`, `testtools.matchers`, Foolscap fURL decoding, Tahoe base32, node config loading, and Ed25519 crypto helpers. Used by tests that assert introducer announcements and node identity.

Risks: `matches_furl`, `matches_nurls`, and `matches_base32` accept any successfully decoded value but do not validate semantic constraints beyond decoding. `MatchesNodePublicKey` reads live config, so changes to test directories between matcher construction and execution affect results.

Test signals: Cover matching and mismatching node keys, malformed fURLs/NURLs/base32 values, anonymous and non-anonymous announcement shapes, storage option list matching, and `MatchesSameElements` mismatch messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/matchers.py -->
