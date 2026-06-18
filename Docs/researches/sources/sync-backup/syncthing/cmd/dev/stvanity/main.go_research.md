# sources/sync-backup/syncthing/cmd/dev/stvanity/main.go

Purpose: development utility that brute-forces a Syncthing TLS certificate whose derived device ID starts with a requested prefix.

Important APIs/types/functions: `result`, `generatePrefixed`, `printProgress`, `saveCert`, `pemBlockForKey`, and `timeStr`. It uses ECDSA P-384 keys, X.509 self-signed certificates, `protocol.NewDeviceID`, goroutines, `sync.WaitGroup`, and atomic counters.

Control flow: normalizes requested prefix, starts progress reporting, launches one certificate generator per `GOMAXPROCS`, waits for the first result, stops workers, then writes `cert.pem` and `key.pem`. Workers reuse one generated private key and repeatedly create certificates with the fixed template until the device ID prefix matches.

State and persistence behavior: writes `cert.pem` and mode-0600 `key.pem` in the current directory. Runtime state includes stop channel, found channel, and generated certificate attempts.

Dependencies/integration: integrates with Syncthing device ID derivation from certificates.

Risks/test signals: search cost grows exponentially at roughly five bits per base32-like prefix character; long prefixes are refused above 63 bits. Reusing the private key while varying certificate DER is intentional but may surprise users. Signal is a matching printed device ID and saved PEM files.
