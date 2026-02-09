set -e
BASE=${BASE:-http://127.0.0.1:8000}

echo "0) Server check"
curl -s "$BASE/openapi.json" >/dev/null && echo "✅ server up"

echo "1) Debug retrieval sanity"
curl -s -X POST "$BASE/debug/retrieve" \
  -H "Content-Type: application/json" \
  -d '{"query":"ng12 visible haematuria 45 and over suspected cancer pathway referral","top_k":8}' | python3 -m json.tool

echo "2) Assess PT-110"
curl -s -X POST "$BASE/assess" \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"PT-110","top_k":5}' | python3 -m json.tool

echo "3) Assess PT-104"
curl -s -X POST "$BASE/assess" \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"PT-104","top_k":5}' | python3 -m json.tool

echo "4) Assess PT-101"
curl -s -X POST "$BASE/assess" \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"PT-101","top_k":5}' | python3 -m json.tool

echo "✅ done"
