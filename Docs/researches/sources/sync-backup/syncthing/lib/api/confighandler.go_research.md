# sources/sync-backup/syncthing/lib/api/confighandler.go

Purpose: Registers and implements REST endpoints for reading and modifying Syncthing configuration.

Important APIs/types/functions: `configMuxBuilder` embeds an `httprouter.Router` and holds device ID plus config wrapper. Register methods cover whole config, deprecated config path, restart status, folders/devices collections and items, defaults, ignores, options, LDAP, and GUI. Adjustment helpers include `adjustConfig`, `adjustFolder`, `adjustDevice`, `adjustOptions`, `adjustGUI`, `postAdjustGui`, `adjustLDAP`, `unmarshalTo`, `unmarshalToRawMessages`, and `finish`.

Control flow: GET handlers return raw config or subsections. PUT collection handlers replace folder/device lists after applying defaults to each raw message. POST collection and PUT item handlers create/replace from defaults; PATCH item handlers merge into existing values. DELETE removes folders/devices. Whole-config and GUI updates call `postAdjustGui` to hash changed cleartext passwords before committing. `finish` waits on the config waiter then saves the config.

State and persistence behavior: Mutates the live config wrapper through `cfg.Modify`, waits for config application, and persists with `cfg.Save`. Password changes are transformed into hashed config values before saving.

Dependencies and integration points: Integrated into the `api.go` router. Depends on config wrapper semantics, `structutil.SetDefaults`, protocol device ID parsing, and JSON decoding.

Risks: `finish` does not explicitly return after save failure, so handlers may have partially written status behavior depending on prior writes. Whole-config modification captures errors inside the modify closure through outer variables. Body reads are unbounded except where callers wrap them. Password hashing depends on detecting a string difference from the existing hashed value.

Test signals: `TestConfigPostOK`, `TestConfigPostDupFolder`, `TestConfigChanges`, and password-change tests in `api_test.go` exercise create, patch, delete, whole-config updates, and GUI password hashing.
