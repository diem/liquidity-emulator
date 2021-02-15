# Diem Liquidity Provider Emulator Helm Chart

## Configuration

- `vaspPrivateKey` - must be always set.
- `diemChainId` and `diemJsonRpc` must be set if running not on testnet.
- `database.create` controls whether the service will use an existing
  database, or a dedicated database service will be deployed.
- `image` and `pullPolicy` control which image and how will be used to
  deploy the liquidity service.
  
More information can be found in `values.yaml`.
