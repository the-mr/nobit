- this project is incomplete and should not be used for end to end encryption.

- The goal of this project was to use a flask webserver running websockets to enable chat functionallity between two clients.
- The server itself would not have access to the private keys being used to encrypt messages.
- Everytime the client booted, a new private and public key would be generated so if the private key was ever stolen only the current chat would be compromised which is never saved on the server. 
