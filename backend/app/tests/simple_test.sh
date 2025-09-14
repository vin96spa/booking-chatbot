#!/bin/bash

BASE_URL="http://localhost:8000"

echo "🚀 Test Semplificato Session ID"

# Test 1: Primo messaggio
echo -e "\n📋 Test 1: Primo messaggio"
echo "Cercando session_id nella risposta..."

RESPONSE1=$(curl -s -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "primo test"}')

echo "Risposta completa:"
echo "$RESPONSE1"

# Estrai session_id in modo più robusto
SESSION_ID=$(echo "$RESPONSE1" | grep -o '"type": "session_id", "data": "[^"]*"' | head -1 | cut -d'"' -f8)

echo -e "\n✅ Session ID estratto: '$SESSION_ID'"

if [ -z "$SESSION_ID" ]; then
    echo "❌ ERRORE: Non riesco a estrarre il session_id"
    echo "Prova manualmente copiando l'ID dalla risposta sopra"
    exit 1
fi

# Test 2: Secondo messaggio
echo -e "\n📋 Test 2: Secondo messaggio con session_id"
echo "Usando session_id: '$SESSION_ID'"

RESPONSE2=$(curl -s -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"secondo test\", \"session_id\": \"$SESSION_ID\"}")

echo "Risposta secondo messaggio:"
echo "$RESPONSE2"

# Estrai session_id dal secondo messaggio
SESSION_ID_2=$(echo "$RESPONSE2" | grep -o '"type": "session_id", "data": "[^"]*"' | head -1 | cut -d'"' -f8)

echo -e "\n🔍 Confronto:"
echo "Session ID 1: '$SESSION_ID'"
echo "Session ID 2: '$SESSION_ID_2'"

if [ "$SESSION_ID" = "$SESSION_ID_2" ]; then
    echo -e "\n✅ SUCCESS: Session ID è consistente!"
else
    echo -e "\n❌ FAIL: Session ID cambia"
fi

# Test 3: Verifica sessione salvata
echo -e "\n📋 Test 3: Verifica sessione"
curl -s -X GET "$BASE_URL/api/sessions/$SESSION_ID" | jq '.' 2>/dev/null || echo "Sessione non trovata o jq non disponibile"
