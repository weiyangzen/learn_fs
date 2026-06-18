# sources/user-network-fs/blobfuse2/cmd/secure_set.go
## sources/user-network-fs/blobfuse2/cmd/secure_set.go

Purpose: implements `blobfuse2 secure set`, updating a scalar value inside an encrypted config and rewriting the encrypted file.

Important APIs/functions: global `setKeyCmd` with `RunE`, `viper.Get`, `viper.Set`, `viper.AllSettings`, `yaml.Marshal`, `common.EncryptData`, and `saveToFile`.

Control flow: the command validates secure options, decrypts the current file into memory, reads it as YAML with Viper, checks the existing value for `secOpts.Key`, rejects map or slice values because only scalar edits are allowed, prints current/target values or an add-new-key message, sets the new value as a string, marshals all Viper settings back to YAML, encrypts the YAML with the same passphrase, and writes ciphertext over `secOpts.ConfigFile` without deleting it.

State and persistence: mutates global Viper and `secOpts`, and persistently rewrites the encrypted config file. YAML output is generated from `viper.AllSettings`, so formatting, key order, comments, and some original scalar types may not be preserved.

Dependencies/integration: Cobra, Viper, `gopkg.in/yaml.v2`, reflection, and `common.EncryptData`.

Risks: all set values are strings, even if the original scalar was boolean or numeric. Re-marshalling through Viper can normalize config shape and drop comments. Direct stdout printing bypasses Cobra output capture. The scalar check uses string prefixes from reflection rather than kind checks.

Test signals: `secure_test.go` covers a get/set/get flow for `logging.level`; it does not assert the changed value text or type preservation.
