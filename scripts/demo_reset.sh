#!/bin/bash
# Pristine demo state: clears repair patches, receipts, stored plans, sabotage (via restart).
rm -f ~/.kerberos/registry_patches.json
rm -rf ~/.kerberos/receipts
rm -f "$(dirname "$0")/../plans"/pln_*.json
echo "State cleared. Restart the app to clear in-memory sabotage: .venv/bin/reflex run --frontend-port 3100 --backend-port 8100"
