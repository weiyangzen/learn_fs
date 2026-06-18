# sources/security-integrity/gocryptfs/internal/configfile/feature_flags.go

Purpose: This file defines gocryptfs feature flags and helpers for recognizing and querying them in config files.

Important APIs and types: `flagIota` enumerates features such as GCM IV size, HKDF, plaintext names, diriv, EME names, longnames, raw64, AES-SIV, FIDO2, long-name max, deterministic names, XChaCha, and related compatibility flags. `knownFlags`, `isFeatureFlagKnown`, and `ConfFile.IsFeatureFlagSet` implement mapping and lookup.

Control flow and state: Feature flags persist as strings in config JSON. Runtime lookup scans `ConfFile.FeatureFlags`.

Dependencies and integration points: Used by config validation, init, mount crypto selection, name encryption behavior, and xray.

Risks and test signals: Feature flags are the on-disk compatibility gate; unknown flags must fail closed and known flags must not be renamed casually. Signals include known-flag tests and fixture validation.
