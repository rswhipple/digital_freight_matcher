#!/bin/sh
#
# test_ordersh [address]
#   args: address: url of server
#

if [ -z "$1" ]
then
    url="http://localhost:5000/receive_order"
else
    url="$1"
fi

curl -X POST -H "Content-Type: application/json" -d '{
    "cargo": {
        "packages": [1, 60, "standard"]
    },
    "pick-up": {
        "latitude": 33.754413815792205,
        "longitude": -84.3875298776525
    },
    "drop-off": {
        "latitude": 34.87433824316913,
        "longitude": -85.08447506395166
    }
}' "$url"
