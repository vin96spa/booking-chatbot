#!/bin/bash

# Configurazione
BASE_URL="http://localhost:8000"
SESSION_ID=""

echo "🚀 Iniziando i test dell'API Frustrating Chatbot"

# 1. Test Health Check
echo -e "\n📋 Test 1: Health Check"
curl -X GET "$BASE_URL/health" \
  -H "Content-Type: application/json" \
  -w "\n"

# 2. Test Root
echo -e "\n📋 Test 2: Root endpoint"
curl -X GET "$BASE_URL/" \
  -H "Content-Type: application/json" \
  -w "\n"

# 3. Primo messaggio (crea una nuova sessione)
echo -e "\n📋 Test 3: Primo messaggio - Creazione sessione"
echo "Invio messaggio: 'Ciao, vorrei prenotare un servizio'"

# Salva la risposta in un file temporaneo
TEMP_FILE="/tmp/chat_response_$$"
curl -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Ciao, vorrei prenotare un servizio"
  }' \
  -N --no-buffer > "$TEMP_FILE" 2>/dev/null

echo "Risposta stream completa:"
cat "$TEMP_FILE"

# Estrai il session_id con regex corretto
SESSION_ID=$(grep -o '"session_id","data":"[^"]*"' "$TEMP_FILE" | head -1 | sed 's/.*"data":"\([^"]*\)".*/\1/')

echo -e "\n✅ Session ID estratto: '$SESSION_ID'"

# Pulisci il file temporaneo
rm -f "$TEMP_FILE"

# Verifica che il session_id non sia vuoto
if [ -z "$SESSION_ID" ]; then
    echo "❌ ERRORE: Session ID non estratto correttamente!"
    exit 1
fi

# 4. Secondo messaggio con session_id esistente
echo -e "\n📋 Test 4: Secondo messaggio - Utilizzo sessione esistente"
echo "Session ID da utilizzare: '$SESSION_ID'"
echo "Invio messaggio: 'Non ho capito, puoi aiutarmi?'"

TEMP_FILE2="/tmp/chat_response2_$$"
curl -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Non ho capito, puoi aiutarmi?\",
    \"session_id\": \"$SESSION_ID\"
  }" \
  -N --no-buffer > "$TEMP_FILE2" 2>/dev/null

cat "$TEMP_FILE2"

# Estrai il session_id dal secondo messaggio
SESSION_ID_2=$(grep -o '"type": "session_id", "data": "[^"]*"' "$TEMP_FILE2" | head -1 | sed 's/.*"data": "\([^"]*\)".*/\1/')

echo -e "\n🔍 Confronto Session ID:"
echo "Primo messaggio:  '$SESSION_ID'"
echo "Secondo messaggio: '$SESSION_ID_2'"

if [ "$SESSION_ID" = "$SESSION_ID_2" ]; then
    echo "✅ SUCCESS: Session ID rimane costante!"
else
    echo "❌ FAIL: Session ID cambia tra messaggi!"
fi

rm -f "$TEMP_FILE2"

# 5. Recupera informazioni della sessione
echo -e "\n📋 Test 5: Recupero informazioni sessione"
curl -X GET "$BASE_URL/api/sessions/$SESSION_ID" \
  -H "Content-Type: application/json" \
  -s | jq '.' 2>/dev/null || curl -X GET "$BASE_URL/api/sessions/$SESSION_ID" -H "Content-Type: application/json"
echo -e "\n"

# 6. Debug - Visualizza tutte le sessioni
echo -e "\n📋 Test 6: Debug - Tutte le sessioni"
curl -X GET "$BASE_URL/api/debug/sessions" \
  -H "Content-Type: application/json" \
  -s | jq '.total_sessions, .sessions' 2>/dev/null || curl -X GET "$BASE_URL/api/debug/sessions" -H "Content-Type: application/json"
echo -e "\n"

# 7. Test cancellazione sessione
echo -e "\n📋 Test 7: Cancellazione sessione"
curl -X DELETE "$BASE_URL/api/sessions/$SESSION_ID" \
  -H "Content-Type: application/json" \
  -w "\n"

echo -e "\n✅ Test completati!"
echo -e "\n📊 RISULTATO FINALE:"
if [ "$SESSION_ID" = "$SESSION_ID_2" ]; then
    echo "✅ Il sistema mantiene correttamente il session_id"
else
    echo "❌ Il sistema ha ancora problemi con la persistenza del session_id"
fi